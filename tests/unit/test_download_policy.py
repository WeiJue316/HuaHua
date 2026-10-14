from research_agent.policy.download import decide_download


def test_open_access_arxiv_pdf_is_allowed() -> None:
    decision = decide_download(
        url="https://arxiv.org/pdf/2407.18940",
        is_open_access=True,
        open_access_status="green",
    )

    assert decision.allowed is True
    assert decision.reason == "open_access"
    assert decision.host == "arxiv.org"


def test_download_policy_rejects_a_host_outside_the_allowlist() -> None:
    decision = decide_download(
        url="https://publisher.example/doi/pdf/10.1000/secret-token",
        is_open_access=True,
        open_access_status="gold",
    )

    assert decision.allowed is False
    assert decision.reason == "host_not_allowed"
    assert decision.host == "publisher.example"
    assert "secret-token" not in decision.host


def test_download_policy_rejects_a_lookalike_arxiv_host() -> None:
    decision = decide_download(
        url="https://evil.arxiv.org/pdf/2407.18940",
        is_open_access=True,
        open_access_status="green",
    )

    assert decision.allowed is False
    assert decision.reason == "host_not_allowed"


def test_download_policy_rejects_closed_access_on_an_allowed_host() -> None:
    decision = decide_download(
        url="https://export.arxiv.org/pdf/2407.18940?token=secret",
        is_open_access=False,
        open_access_status="closed",
    )

    assert decision.allowed is False
    assert decision.reason == "not_open_access"
    assert decision.host == "export.arxiv.org"
    assert "secret" not in decision.reason


def test_gold_status_allows_download_without_the_open_access_flag() -> None:
    decision = decide_download(
        url="https://www.arxiv.org/pdf/2407.18940",
        is_open_access=False,
        open_access_status="gold",
    )

    assert decision.allowed is True
    assert decision.host == "www.arxiv.org"


def test_redirect_host_is_checked_again() -> None:
    decision = decide_download(
        url="https://publisher.example/final.pdf",
        is_open_access=True,
        open_access_status="green",
    )

    assert decision.allowed is False
    assert decision.reason == "host_not_allowed"
