import unittest

from rotated_consensus.domain import ClaimStatus, ClaimVerdict, Verdict
from rotated_consensus.merge import classify, flat_majority, strict_majority_floor


def vote(verdict: Verdict, confidence: float = 0.8) -> ClaimVerdict:
    return ClaimVerdict(verdict, confidence)


class MergeTests(unittest.TestCase):
    def test_unanimous_positions_are_converged(self) -> None:
        verdicts = [vote(Verdict.ASSERT) for _ in range(3)]
        self.assertIs(classify(verdicts, expected_engine_count=3), ClaimStatus.CONVERGED)

    def test_historical_strong_dissent_downgrades_unanimity(self) -> None:
        verdicts = [vote(Verdict.ASSERT) for _ in range(3)]
        result = classify(
            verdicts,
            expected_engine_count=3,
            historical_dissent_confidences=[0.9],
        )
        self.assertIs(result, ClaimStatus.MAJORITY)

    def test_degraded_quorum_is_not_reported_as_convergence(self) -> None:
        verdicts = [vote(Verdict.ASSERT), vote(Verdict.ASSERT)]
        self.assertIs(classify(verdicts, expected_engine_count=3), ClaimStatus.MAJORITY)

    def test_split_without_strict_majority_is_diverged(self) -> None:
        verdicts = [vote(Verdict.ASSERT), vote(Verdict.DENY)]
        self.assertIs(classify(verdicts, expected_engine_count=2), ClaimStatus.DIVERGED)

    def test_majority_floor_is_strict_for_even_engine_counts(self) -> None:
        self.assertEqual(strict_majority_floor(3), 2)
        self.assertEqual(strict_majority_floor(4), 3)

    def test_flat_majority_reports_ties(self) -> None:
        self.assertIsNone(flat_majority([Verdict.ASSERT, Verdict.DENY]))


if __name__ == "__main__":
    unittest.main()
