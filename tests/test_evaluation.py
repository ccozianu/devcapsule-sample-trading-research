import unittest

from rotated_consensus.domain import ClaimStatus
from rotated_consensus.evaluation import EvaluationRecord, evaluate


class EvaluationTests(unittest.TestCase):
    def test_report_groups_accuracy_by_epistemic_state(self) -> None:
        report = evaluate(
            [
                EvaluationRecord("a", ClaimStatus.CONVERGED, True, 3),
                EvaluationRecord("b", ClaimStatus.CONVERGED, False, 3),
                EvaluationRecord("c", ClaimStatus.DIVERGED, True, 3),
            ]
        )
        by_status = {row.status: row for row in report.by_status}
        self.assertEqual(by_status[ClaimStatus.CONVERGED].accuracy, 0.5)
        self.assertEqual(by_status[ClaimStatus.DIVERGED].accuracy, 1.0)
        self.assertEqual(report.total_llm_calls, 9)

    def test_report_distinguishes_capitulation_from_reasoned_concession(self) -> None:
        report = evaluate(
            [EvaluationRecord("a", ClaimStatus.MAJORITY, True, 24, 1, 3)]
        )
        self.assertEqual(report.capitulation_rate, 0.25)


if __name__ == "__main__":
    unittest.main()
