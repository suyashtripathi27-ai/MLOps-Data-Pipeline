class Scorecard:
    def __init__(self):
        self.scores = {
            "behavioral_intelligence": 0,
            "prioritization": 0,
            "recommendation_traceability": 0, # 👈 Added V2 Metric
            "governance": 0,
            "executive_readability": 0,
            "industry_realism": 0
        }
        self.max_score = 60 # 👈 Updated for V2

    def get_total_score(self):
        return sum(self.scores.values())

    def get_percentage(self):
        return round((self.get_total_score() / self.max_score) * 100, 2)

    def get_report(self):
        return {
            "total_score": self.get_total_score(),
            "max_score": self.max_score,
            "percentage": self.get_percentage(),
            "dimensions": self.scores
        }
