class NewsSentimentAnalyzer:
    """
    Performs a simple, transparent sentiment analysis
    on supplied financial news headlines.

    This is a development-level sentiment analyzer.
    It is not a substitute for professional financial
    research or a trained financial NLP model.
    """

    def __init__(self):
        self.positive_words = {
            "growth",
            "strong",
            "profit",
            "profits",
            "positive",
            "expansion",
            "increase",
            "increased",
            "rises",
            "rise",
            "gains",
            "gain",
            "improves",
            "improvement",
            "demand",
            "success",
            "successful",
        }

        self.negative_words = {
            "loss",
            "losses",
            "weak",
            "negative",
            "decline",
            "declines",
            "decrease",
            "decreased",
            "falls",
            "fall",
            "drop",
            "drops",
            "risk",
            "warning",
            "debt",
            "concern",
            "concerns",
            "downturn",
        }

    def analyze_article(self, article):
        """
        Analyzes one news article.
        """

        headline = article.get("headline", "")
        summary = article.get("summary", "")

        text = f"{headline} {summary}".lower()

        words = text.replace(",", " ").replace(".", " ").split()

        positive_count = 0
        negative_count = 0

        for word in words:
            if word in self.positive_words:
                positive_count += 1

            if word in self.negative_words:
                negative_count += 1

        if positive_count > negative_count:
            sentiment = "Positive"

        elif negative_count > positive_count:
            sentiment = "Negative"

        else:
            sentiment = "Neutral"

        return {
            "headline": headline,
            "sentiment": sentiment,
            "positive_count": positive_count,
            "negative_count": negative_count,
        }

    def analyze(self, news):
        """
        Analyzes all supplied news articles.
        """

        if not news:
            return {
                "sentiment": "Neutral",
                "sentiment_score": 50,
                "articles_analyzed": 0,
                "articles": [],
            }

        analyzed_articles = []

        for article in news:
            result = self.analyze_article(article)
            analyzed_articles.append(result)

        positive_articles = 0
        negative_articles = 0

        for article in analyzed_articles:
            if article["sentiment"] == "Positive":
                positive_articles += 1

            elif article["sentiment"] == "Negative":
                negative_articles += 1

        total_articles = len(analyzed_articles)

        if positive_articles > negative_articles:
            overall_sentiment = "Positive"

        elif negative_articles > positive_articles:
            overall_sentiment = "Negative"

        else:
            overall_sentiment = "Neutral"

        sentiment_score = (
            50
            + (positive_articles / total_articles) * 50
            - (negative_articles / total_articles) * 50
        )

        sentiment_score = max(
            0,
            min(100, sentiment_score),
        )

        return {
            "sentiment": overall_sentiment,
            "sentiment_score": round(
                sentiment_score,
                2,
            ),
            "articles_analyzed": total_articles,
            "articles": analyzed_articles,
        }