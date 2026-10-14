#!/usr/bin/env python3
"""Install and check the web app when Node.js is available.

Without Node.js this command exits 0, so the Python checks can still pass.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def main() -> int:
    """Return 0 when the web checks pass or Node.js is absent."""

    npm = shutil.which("npm")
    node = shutil.which("node")
    if npm is None or node is None:
        print("WEB_CHECKS_SKIPPED no Node.js")
        return 0

    for args in (["ci"], ["run", "check"]):
        print(f"$ npm {' '.join(args)}", flush=True)
        completed = subprocess.run([npm, *args], cwd=WEB, check=False)
        if completed.returncode != 0:
            print("WEB_CHECKS_FAILED")
            return completed.returncode
    print("WEB_CHECKS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
