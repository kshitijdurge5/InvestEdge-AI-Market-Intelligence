class ScoringEngine:

    def calculate_score(self, analysis):
        momentum_score = analysis["momentum_score"]

        if analysis["trend"] == "Positive":
            trend_score = 80
        elif analysis["trend"] == "Neutral":
            trend_score = 60
        else:
            trend_score = 40

        if analysis["volume_status"] == "High":
            volume_score = 80
        elif analysis["volume_status"] == "Moderate":
            volume_score = 60
        else:
            volume_score = 40

        overall_score = (
            momentum_score * 0.5
            + trend_score * 0.3
            + volume_score * 0.2
        )

        return {
            "symbol": analysis["symbol"],
            "momentum_score": momentum_score,
            "trend_score": trend_score,
            "volume_score": volume_score,
            "overall_score": round(overall_score, 2),
        }