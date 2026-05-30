class Scorecard:
    def __init__(self):
        self.scores = {
            "behavioral_intelligence": 0,
            "prioritization": 0,
            "governance": 0,
            "executive_readability": 0,
            "industry_realism": 0,
            "numerical_accuracy": "NOT_IMPLEMENTED" 
        }
        self.max_score_per_dim = 10

    def calculate_total(self):
        active_scores = [v for v in self.scores.values() if isinstance(v, (int, float))]
        total = sum(active_scores)
        max_total = len(active_scores) * self.max_score_per_dim
        return total, max_total

    def get_report(self):
        total, max_total = self.calculate_total()
        report = {"dimensions": self.scores.copy(), "total_score": total, "max_score": max_total}
        report["percentage"] = round((total / max_total) * 100, 2) if max_total > 0 else 0
        return report
