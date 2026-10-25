"""
InvestEdge UI - Reusable Components

Small HTML helpers used by the InvestEdge dashboard.

This file intentionally contains presentation helpers only.
It does not call the API and does not perform market analysis.
"""

from html import escape
from typing import Any


def _safe(value: Any, fallback: str = "—") -> str:
    """Convert a value to safe HTML text."""
    if value is None or value == "":
        return fallback

    return escape(str(value))


def _number(value: Any, digits: int = 2, fallback: str = "—") -> str:
    """Format a numeric value safely."""
    if value is None or value == "":
        return fallback

    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return _safe(value, fallback)


def _percent(value: Any, digits: int = 2) -> str:
    """Format a percentage."""
    if value is None or value == "":
        return "—"

    try:
        number = float(value)
        sign = "+" if number > 0 else ""
        return f"{sign}{number:,.{digits}f}%"
    except (TypeError, ValueError):
        return _safe(value)


def _score_class(value: Any) -> str:
    """Return a visual score class."""
    try:
        score = float(value)

        if score >= 70:
            return "metric-positive"

        if score >= 50:
            return "metric-warning"

        return "metric-negative"

    except (TypeError, ValueError):
        return "metric-neutral"


def _signal_class(signal: Any) -> str:
    """Return a visual class for a unified market signal."""
    value = str(signal or "").strip().lower()

    if value in {"positive", "bullish", "strong positive"}:
        return "metric-positive"

    if value in {"negative", "bearish", "strong negative"}:
        return "metric-negative"

    if value in {"mixed", "partially aligned"}:
        return "metric-warning"

    return "metric-neutral"


def _agreement_class(agreement: Any) -> str:
    """Return a visual class for AI/model agreement."""
    value = str(agreement or "").strip().lower()

    if value in {"high", "strong"}:
        return "metric-positive"

    if value in {"moderate", "medium"}:
        return "metric-warning"

    if value in {"low", "weak"}:
        return "metric-negative"

    return "metric-neutral"


def metric_card(
    label: str,
    value: Any,
    *,
    subvalue: str = "",
    value_class: str = "",
    icon: str = "",
) -> str:
    """
    Create a dashboard metric card.
    """

    icon_html = ""

    if icon:
        icon_html = f"""
        <span style="
            margin-left:8px;
            font-size:15px;
            opacity:0.75;
        ">{escape(icon)}</span>
        """

    return f"""
    <div class="metric-card">
        <div class="metric-label">
            {escape(label)}
            {icon_html}
        </div>

        <div class="metric-value {value_class}">
            {value}
        </div>

        {
            f'<div class="metric-subvalue">{escape(subvalue)}</div>'
            if subvalue
            else ""
        }
    </div>
    """


def price_card(price: Any) -> str:
    """Create the current price card."""

    if price is None:
        formatted = "—"
    else:
        try:
            formatted = f"₹{float(price):,.2f}"
        except (TypeError, ValueError):
            formatted = _safe(price)

    return metric_card(
        "Current Price",
        formatted,
        icon="₹",
    )


def change_card(change: Any) -> str:
    """Create the daily price-change card."""

    try:
        number = float(change)

        if number > 0:
            css_class = "metric-positive"
            icon = "↑"
        elif number < 0:
            css_class = "metric-negative"
            icon = "↓"
        else:
            css_class = "metric-neutral"
            icon = "→"

    except (TypeError, ValueError):
        css_class = "metric-neutral"
        icon = ""

    return metric_card(
        "Change",
        _percent(change),
        value_class=css_class,
        icon=icon,
    )


def signal_card(
    signal: Any,
    *,
    consistency: str = "",
    market_signal: str = "",
    technical_signal: str = "",
) -> str:
    """
    Create the unified signal card.

    The purpose is to make the signal understandable without
    requiring the user to understand the scoring engine.
    """

    signal_text = _safe(signal)

    css_class = _signal_class(signal)

    descriptions = {
        "positive":
            "Market and technical evidence is generally supportive.",
        "negative":
            "Market and technical evidence is generally weak.",
        "mixed":
            "Different signals are pointing in different directions.",
        "neutral":
            "The available evidence does not show a strong direction.",
    }

    description = descriptions.get(
        str(signal or "").strip().lower(),
        "Review the supporting evidence before making a decision.",
    )

    supporting = []

    if market_signal:
        supporting.append(
            f"Market: {_safe(market_signal)}"
        )

    if technical_signal:
        supporting.append(
            f"Technical: {_safe(technical_signal)}"
        )

    support_text = " • ".join(supporting)

    return f"""
    <div class="signal-card">
        <div class="signal-layout">

            <div class="signal-main">

                <div class="signal-icon">
                    🧭
                </div>

                <div>
                    <div class="signal-title">
                        Unified Market Signal
                    </div>

                    <div class="signal-value {css_class}">
                        {signal_text}
                    </div>

                    <div class="signal-description">
                        {escape(description)}
                    </div>

                    {
                        f'''
                        <div class="signal-description"
                             style="margin-top:8px;">
                            {support_text}
                        </div>
                        '''
                        if support_text
                        else ""
                    }

                </div>

            </div>

            {
                f'''
                <div class="metric-subvalue"
                     style="text-align:right;">
                    Signal consistency<br>
                    <strong style="color:white;">
                        {_safe(consistency)}
                    </strong>
                </div>
                '''
                if consistency
                else ""
            }

        </div>
    </div>
    """


def score_breakdown_table(breakdown: Any) -> str:
    """
    Create the deterministic score breakdown table.

    Expected structure:

    {
        "market": {
            "score": 70,
            "weight": 0.25,
            "contribution": 17.5
        },
        ...
    }
    """

    if not isinstance(breakdown, dict) or not breakdown:
        return """
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h3 class="empty-title">
                Score breakdown unavailable
            </h3>
            <p class="empty-text">
                Component-level scoring information was not returned.
            </p>
        </div>
        """

    labels = {
        "market": "Market",
        "technical": "Technical",
        "fundamental": "Fundamental",
        "risk": "Risk",
        "news": "News & Sentiment",
    }

    rows = []

    for key, label in labels.items():

        component = breakdown.get(key, {})

        if not isinstance(component, dict):
            component = {}

        score = component.get("score")
        weight = component.get("weight")
        contribution = component.get("contribution")

        try:
            score_number = float(score)
            bar_width = max(
                0,
                min(
                    100,
                    score_number,
                ),
            )
        except (TypeError, ValueError):
            bar_width = 0

        rows.append(
            f"""
            <tr>

                <td>
                    {escape(label)}
                </td>

                <td>
                    <strong style="color:white;">
                        {_number(score)}
                    </strong>

                    <div class="score-bar"
                         style="margin-top:7px;">

                        <div
                            class="score-bar-fill"
                            style="width:{bar_width:.0f}%;">
                        </div>

                    </div>
                </td>

                <td>
                    {_number(
                        float(weight) * 100
                        if weight is not None
                        else None,
                        0
                    )}%
                </td>

                <td>
                    {_number(contribution)}
                </td>

            </tr>
            """
        )

    return f"""
    <div class="breakdown-card">

        <table class="breakdown-table">

            <thead>
                <tr>
                    <th>Component</th>
                    <th>Score</th>
                    <th>Weight</th>
                    <th>Contribution</th>
                </tr>
            </thead>

            <tbody>
                {"".join(rows)}
            </tbody>

        </table>

    </div>
    """


def info_card(
    title: str,
    rows: list[tuple[str, Any]],
    *,
    icon: str = "",
) -> str:
    """Create a simple information card."""

    icon_html = (
        f'<span style="margin-right:7px;">{escape(icon)}</span>'
        if icon
        else ""
    )

    row_html = []

    for label, value in rows:

        row_html.append(
            f"""
            <div class="info-row">

                <div class="info-label">
                    {escape(str(label))}
                </div>

                <div class="info-value">
                    {_safe(value)}
                </div>

            </div>
            """
        )

    return f"""
    <div class="info-card">

        <h3 class="info-card-title">
            {icon_html}
            {escape(title)}
        </h3>

        {"".join(row_html)}

    </div>
    """


def tags(items: Any) -> str:
    """Render a collection of small tags."""

    if not items:
        return ""

    if isinstance(items, str):
        items = [items]

    try:
        values = list(items)
    except TypeError:
        values = [items]

    rendered = []

    for item in values:

        if item is None:
            continue

        rendered.append(
            f'<span class="tag">{escape(str(item))}</span>'
        )

    if not rendered:
        return ""

    return f"""
    <div class="tags">
        {"".join(rendered)}
    </div>
    """


def list_items(items: Any) -> str:
    """Render a clean list for risks, events, observations, etc."""

    if not items:
        return """
        <div class="empty-text">
            No specific items were returned.
        </div>
        """

    if isinstance(items, str):
        items = [items]

    try:
        values = list(items)
    except TypeError:
        values = [items]

    html_items = []

    for item in values:

        if item is None:
            continue

        html_items.append(
            f"""
            <li style="
                margin-bottom:8px;
                color:#d8e3ea;
                line-height:1.55;
            ">
                {escape(str(item))}
            </li>
            """
        )

    if not html_items:
        return """
        <div class="empty-text">
            No specific items were returned.
        </div>
        """

    return f"""
    <ul style="
        margin:0;
        padding-left:20px;
    ">
        {"".join(html_items)}
    </ul>
    """


def ai_report_card(report: Any) -> str:
    """Create the AI research report panel."""

    if report is None:
        report = "No AI research report was returned."

    if isinstance(report, dict):
        parts = []

        for key, value in report.items():

            title = str(key).replace("_", " ").title()

            parts.append(
                f"""
                <div style="margin-bottom:18px;">

                    <div style="
                        color:#8cecff;
                        font-size:11px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:0.7px;
                        margin-bottom:5px;
                    ">
                        {escape(title)}
                    </div>

                    <div>
                        {escape(str(value))}
                    </div>

                </div>
                """
            )

        report_html = "".join(parts)

    else:
        report_html = escape(str(report))

    return f"""
    <div class="ai-report">

        <div class="ai-report-header">

            <div class="ai-report-icon">
                🤖
            </div>

            <div>
                <h3 class="ai-report-title">
                    InvestEdge AI Research
                </h3>

                <div class="metric-subvalue">
                    AI-generated interpretation of the available evidence
                </div>
            </div>

        </div>

        <div class="ai-report-body">
            {report_html}
        </div>

    </div>
    """


def development_warning() -> str:
    """Render the development/mock-data warning."""

    return """
    <div class="development-warning">
        <span style="font-size:17px;">⚠️</span>

        <span>
            <strong>Development mode:</strong>
            some market, historical and news data may be
            mock/synthetic data. Replace these providers with
            live market data before using InvestEdge for real
            investment decisions.
        </span>
    </div>
    """


def loading_state() -> str:
    """Render the loading indicator."""

    return """
    <div id="loading" class="loading">

        <div class="loading-spinner"></div>

        <div style="
            color:white;
            font-weight:700;
            margin-bottom:5px;
        ">
            Analyzing the market...
        </div>

        <div style="
            color:#718494;
            font-size:12px;
        ">
            InvestEdge is combining market, technical,
            fundamental, risk and AI research.
        </div>

    </div>
    """


def error_state() -> str:
    """Render the hidden error container."""

    return """
    <div id="error" class="error-box"></div>
    """


def empty_state() -> str:
    """Render the initial dashboard state."""

    return """
    <div id="emptyState" class="empty-state">

        <div class="empty-icon">
            📈
        </div>

        <h3 class="empty-title">
            Start with a stock
        </h3>

        <p class="empty-text">
            Enter an NSE stock symbol above or choose one
            of the popular stocks to see a complete
            InvestEdge market analysis.
        </p>

    </div>
    """


__all__ = [
    "_safe",
    "_number",
    "_percent",
    "_score_class",
    "_signal_class",
    "_agreement_class",
    "metric_card",
    "price_card",
    "change_card",
    "signal_card",
    "score_breakdown_table",
    "info_card",
    "tags",
    "list_items",
    "ai_report_card",
    "development_warning",
    "loading_state",
    "error_state",
    "empty_state",
]