import pytest

from research_agent.evaluator.ranking import candidate_list, interleave_by_source


def test_interleave_takes_one_hit_from_each_source_in_turn() -> None:
    merged = interleave_by_source(
        (
            ("a1", "a2", "a3"),
            ("b1", "b2"),
        )
    )

    assert merged == ["a1", "b1", "a2", "b2", "a3"]


def test_interleave_skips_a_duplicate_without_promoting_the_next_hit() -> None:
    merged = interleave_by_source(
        (
            ("p1", "p2"),
            ("p1", "p4"),
        )
    )

    assert merged == ["p1", "p2", "p4"]


def test_candidate_list_drops_filtered_papers_and_truncates_to_k() -> None:
    ranked = candidate_list(
        ("a1", "b1", "a2", "b2", "a3"),
        dropped={"b1"},
        k=3,
    )

    assert ranked == ["a1", "a2", "b2"]


def test_candidate_list_rejects_a_negative_k() -> None:
    with pytest.raises(ValueError, match="k"):
        candidate_list(("a1",), k=-1)
