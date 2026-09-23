"""Filesystem cache for source HTTP responses.

Why this exists: a keyword search run twice does not return the same papers.
Limiting request rates stops rejections but does not stop the API from
answering differently, so ablation arms that each issue their own requests end
up comparing different inputs. Caching makes the input identical.

The cache is content-addressed and lives on the filesystem, consistent with the
project's local-first, immutable-file choice, and it needs no schema change.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import httpx

DEFAULT_TTL_SECONDS: float = 7 * 24 * 60 * 60
CACHEABLE_STATUS = range(200, 300)

# httpx hands back an already-decoded body, so storing the original
# content-encoding makes the replay try to decode it a second time and fail
# with "incorrect header check". Length and transfer framing are equally
# meaningless once the body is stored decoded.
HEADERS_NOT_TO_REPLAY = frozenset(
    {"content-encoding", "content-length", "transfer-encoding"}
)


@dataclass(frozen=True)
class CacheStats:
    """Hit and miss counters for one cache instance."""

    hits: int = 0
    misses: int = 0

    def to_dict(self) -> dict[str, int]:
        return {"cache_hits": self.hits, "cache_misses": self.misses}


def cache_key(method: str, url: str) -> str:
    """Return the storage key for one request.

    Authentication headers are deliberately excluded: an API key changes the
    quota, not the content. The URL already carries every parameter that does.
    """

    return hashlib.sha256(f"{method.upper()}\n{url}".encode()).hexdigest()


class ResponseCache:
    """Store successful source responses and replay them on demand.

    Only 2xx responses are stored. Caching a failure would freeze one transient
    429 into a permanent failure for the whole evaluation window.
    """

    def __init__(
        self,
        root: Path,
        *,
        ttl_seconds: float | None = DEFAULT_TTL_SECONDS,
    ) -> None:
        self.root = Path(root)
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> CacheStats:
        return CacheStats(hits=self._hits, misses=self._misses)

    def reset_stats(self) -> None:
        self._hits = 0
        self._misses = 0

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, *, method: str, url: str, now: float) -> httpx.Response | None:
        """Return a stored response, or None when the request is a miss."""

        path = self._path(cache_key(method, url))
        if not path.is_file():
            self._misses += 1
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._misses += 1
            return None
        stored_at = payload.get("stored_at")
        if not isinstance(stored_at, (int, float)):
            self._misses += 1
            return None
        if self.ttl_seconds is not None and now - stored_at > self.ttl_seconds:
            self._misses += 1
            return None
        try:
            content = base64.b64decode(payload["content_b64"])
        except (KeyError, ValueError, TypeError):
            self._misses += 1
            return None
        self._hits += 1
        headers = {
            str(k): str(v)
            for k, v in (payload.get("headers") or {}).items()
            if str(k).lower() not in HEADERS_NOT_TO_REPLAY
        }
        return httpx.Response(
            status_code=int(payload.get("status_code", 200)),
            content=content,
            headers=headers,
            request=httpx.Request(method.upper(), url),
        )

    def put(
        self,
        *,
        method: str,
        url: str,
        response: httpx.Response,
        now: float,
    ) -> None:
        """Store a successful response. Failures are not cached."""

        if response.status_code not in CACHEABLE_STATUS:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        payload = {
            "method": method.upper(),
            "url": url,
            "status_code": response.status_code,
            "headers": {
                key: value
                for key, value in response.headers.items()
                if key.lower() not in HEADERS_NOT_TO_REPLAY
            },
            "content_b64": base64.b64encode(response.content).decode("ascii"),
            "stored_at": now,
        }
        path = self._path(cache_key(method, url))
        # written whole, then moved into place, so a crash cannot leave a
        # half-written entry that later reads as valid
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        temporary.replace(path)

    def directory_hash(self) -> str:
        """Hash of every entry's key and content.

        Timestamps are excluded so that re-running a warm cache does not change
        the hash, while any change to a stored response does.
        """

        if not self.root.is_dir():
            return hashlib.sha256(b"").hexdigest()
        digest = hashlib.sha256()
        for path in sorted(self.root.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                content = base64.b64decode(payload.get("content_b64", ""))
            except (OSError, json.JSONDecodeError, ValueError, TypeError):
                digest.update(path.name.encode())
                digest.update(b"corrupt")
                continue
            digest.update(path.stem.encode())
            digest.update(hashlib.sha256(content).digest())
        return digest.hexdigest()

    def entry_count(self) -> int:
        if not self.root.is_dir():
            return 0
        return sum(1 for _ in self.root.glob("*.json"))