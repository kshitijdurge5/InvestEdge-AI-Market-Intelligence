from fastapi.responses import HTMLResponse


def research_page() -> HTMLResponse:
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>InvestEdge — Stock Research</title>

<style>

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    font-family:
        Inter,
        Segoe UI,
        Arial,
        sans-serif;

    background: #07111f;
    color: #eef5ff;
}

button,
input {
    font: inherit;
}

button {
    -webkit-tap-highlight-color: transparent;
}

.page {
    min-height: 100vh;

    background:
        radial-gradient(
            circle at 85% 10%,
            rgba(34,197,94,.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 10% 30%,
            rgba(59,130,246,.10),
            transparent 30%
        ),
        #07111f;
}


/* =========================================================
   TOP BAR
   ========================================================= */

.topbar {

    height: 72px;

    padding: 0 28px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-bottom:
        1px solid rgba(255,255,255,.08);

    background:
        rgba(7,17,31,.92);

    position: sticky;

    top: 0;

    z-index: 20;

    backdrop-filter: blur(16px);
}

.brand {

    display: flex;

    align-items: center;

    gap: 12px;
}

.logo {

    width: 40px;
    height: 40px;

    border-radius: 12px;

    display: grid;

    place-items: center;

    background:
        linear-gradient(
            135deg,
            #22c55e,
            #16a34a
        );

    color: white;

    font-weight: 900;

    box-shadow:
        0 8px 25px rgba(34,197,94,.20);
}

.brand-title {

    font-weight: 800;

    font-size: 18px;
}

.brand-sub {

    font-size: 10px;

    color: #7f91a8;

    letter-spacing: 1.5px;

    margin-top: 2px;
}

.actions {

    display: flex;

    gap: 10px;
}

.btn {

    border:
        1px solid rgba(255,255,255,.10);

    background: #101d2f;

    color: #eaf2ff;

    padding: 10px 16px;

    border-radius: 10px;

    cursor: pointer;

    transition:
        background .2s ease,
        transform .2s ease;
}

.btn:hover {

    background: #17283e;

    transform: translateY(-1px);
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.container {

    max-width: 1280px;

    margin: auto;

    padding: 28px;
}


/* =========================================================
   SEARCH
   ========================================================= */

.search-box {

    display: flex;

    gap: 10px;

    margin-bottom: 24px;
}

.search-box input {

    flex: 1;

    min-width: 0;

    background: #0d1a2b;

    border:
        1px solid rgba(255,255,255,.10);

    color: white;

    padding: 15px 18px;

    border-radius: 12px;

    outline: none;

    transition:
        border .2s ease,
        box-shadow .2s ease;
}

.search-box input:focus {

    border-color: #22c55e;

    box-shadow:
        0 0 0 3px rgba(34,197,94,.10);
}

.search-btn {

    background: #22c55e;

    color: #04110a;

    border: 0;

    padding: 0 24px;

    border-radius: 12px;

    font-weight: 800;

    cursor: pointer;

    transition:
        transform .2s ease,
        background .2s ease;
}

.search-btn:hover {

    background: #34d36b;

    transform: translateY(-1px);
}


/* =========================================================
   HERO
   ========================================================= */

.hero-card {

    background:
        linear-gradient(
            135deg,
            #102238,
            #0b1728
        );

    border:
        1px solid rgba(255,255,255,.08);

    border-radius: 20px;

    padding: 26px;

    margin-bottom: 18px;

    box-shadow:
        0 20px 60px rgba(0,0,0,.20);
}

.stock-head {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 20px;
}

.stock-name {

    font-size: 27px;

    font-weight: 850;

    line-height: 1.2;
}

.stock-symbol {

    color: #8da0b8;

    margin-top: 5px;

    font-size: 13px;
}

.price {

    font-size: 32px;

    font-weight: 850;

    margin-top: 15px;
}

.change {

    margin-left: 10px;

    font-size: 15px;

    font-weight: 700;
}

.positive {

    color: #4ade80;
}

.negative {

    color: #fb7185;
}

.neutral {

    color: #fbbf24;
}


/* =========================================================
   SIGNAL BOX
   ========================================================= */

.signal {

    min-width: 190px;

    text-align: center;

    padding: 18px;

    border-radius: 16px;

    background:
        rgba(251,191,36,.10);

    border:
        1px solid rgba(251,191,36,.25);

    box-shadow:
        0 10px 30px rgba(0,0,0,.15);
}

.signal-label {

    font-size: 12px;

    color: #9eafc5;

    letter-spacing: 1px;
}

.signal-value {

    font-size: 30px;

    font-weight: 900;

    margin-top: 4px;
}

.score {

    margin-top: 6px;

    color: #a9bad0;

    font-size: 13px;
}


/* =========================================================
   DATA SOURCE
   ========================================================= */

.live-status {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    margin-top: 12px;

    padding: 6px 10px;

    border-radius: 999px;

    background:
        rgba(34,197,94,.08);

    border:
        1px solid rgba(34,197,94,.18);

    color: #65e58d;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: .4px;
}

.live-dot {

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #22c55e;

    box-shadow:
        0 0 10px rgba(34,197,94,.8);
}


/* =========================================================
   GENERAL GRID
   ========================================================= */

.grid {

    display: grid;

    grid-template-columns:
        repeat(5, 1fr);

    gap: 14px;

    margin-bottom: 18px;
}

.card {

    background: #0c192a;

    border:
        1px solid rgba(255,255,255,.07);

    border-radius: 16px;

    padding: 18px;

    transition:
        transform .2s ease,
        border .2s ease;
}

.card:hover {

    transform: translateY(-2px);

    border-color:
        rgba(255,255,255,.13);
}

.card-title {

    color: #8ea1b8;

    font-size: 12px;

    margin-bottom: 10px;

    letter-spacing: .5px;
}

.card-value {

    font-size: 22px;

    font-weight: 800;
}

.card-small {

    margin-top: 5px;

    font-size: 12px;

    color: #7f91a8;

    line-height: 1.5;
}


/* =========================================================
   PANELS
   ========================================================= */

.section-grid {

    display: grid;

    grid-template-columns:
        1.15fr .85fr;

    gap: 18px;

    margin-bottom: 18px;
}

.panel {

    background: #0c192a;

    border:
        1px solid rgba(255,255,255,.07);

    border-radius: 18px;

    padding: 22px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.08);
}

.panel h2 {

    margin: 0 0 18px;

    font-size: 17px;
}


/* =========================================================
   SIGNAL ROWS
   ========================================================= */

.signal-row {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 15px;

    padding: 13px 0;

    border-bottom:
        1px solid rgba(255,255,255,.06);
}

.signal-row:last-child {

    border-bottom: 0;
}

.badge {

    padding: 6px 10px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 800;

    white-space: nowrap;
}

.badge.green {

    color: #4ade80;

    background:
        rgba(34,197,94,.12);
}

.badge.red {

    color: #fb7185;

    background:
        rgba(244,63,94,.12);
}

.badge.yellow {

    color: #fbbf24;

    background:
        rgba(251,191,36,.12);
}


/* =========================================================
   METRICS
   ========================================================= */

.metric-grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 12px;
}

.metric {

    background: #101f33;

    padding: 14px;

    border-radius: 12px;

    border:
        1px solid rgba(255,255,255,.03);
}

.metric span {

    display: block;

    color: #8295ad;

    font-size: 11px;

    margin-bottom: 6px;
}

.metric strong {

    font-size: 17px;

    line-height: 1.3;
}


/* =========================================================
   CONFIDENCE
   ========================================================= */

.confidence-panel {

    margin-bottom: 18px;
}

.confidence-track {

    width: 100%;

    height: 14px;

    background: #172235;

    border-radius: 20px;

    overflow: hidden;

    margin: 14px 0;
}

.confidence-fill {

    height: 100%;

    border-radius: 20px;

    background:
        linear-gradient(
            90deg,
            #fbbf24,
            #22c55e
        );

    transition:
        width .6s ease;
}

.confidence-labels {

    display: flex;

    justify-content: space-between;

    color: #8da0b8;

    font-size: 12px;
}


/* =========================================================
   CHART
   ========================================================= */

.chart-panel {

    margin-bottom: 18px;
}

#chart {

    width: 100%;

    height: 300px;

    display: block;

    background: #091525;

    border-radius: 14px;
}


/* =========================================================
   AI
   ========================================================= */

.ai {

    line-height: 1.7;

    color: #b9c7d8;

    background:
        linear-gradient(
            135deg,
            #0d2035,
            #0b1728
        );

    margin-bottom: 18px;
}

.ai-title {

    display: flex;

    align-items: center;

    gap: 8px;
}


/* =========================================================
   NEWS
   ========================================================= */

.news-item {

    padding: 13px 0;

    border-bottom:
        1px solid rgba(255,255,255,.06);
}

.news-item:last-child {

    border-bottom: 0;
}

.news-title {

    font-weight: 700;

    line-height: 1.45;
}

.news-meta {

    font-size: 11px;

    color: #7f91a8;

    margin-top: 5px;

    line-height: 1.5;
}


/* =========================================================
   LOADING / ERROR
   ========================================================= */

.loading,
.error {

    text-align: center;

    padding: 60px 20px;

    color: #91a4bb;
}

.error {

    color: #fb7185;

    background:
        rgba(244,63,94,.05);

    border:
        1px solid rgba(244,63,94,.15);

    border-radius: 16px;
}


/* =========================================================
   DISCLAIMER
   ========================================================= */

.disclaimer {

    margin-top: 18px;

    padding: 14px;

    border-radius: 12px;

    background:
        rgba(34,197,94,.05);

    border:
        1px solid rgba(34,197,94,.12);

    color: #9fb5a8;

    font-size: 12px;

    line-height: 1.6;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1050px) {

    .grid {

        grid-template-columns:
            repeat(3, 1fr);
    }
}

@media (max-width: 900px) {

    .grid {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .section-grid {

        grid-template-columns: 1fr;
    }
}

@media (max-width: 600px) {

    .topbar {

        padding: 0 14px;

        height: 64px;
    }

    .container {

        padding: 16px;
    }

    .brand-sub {

        display: none;
    }

    .stock-head {

        align-items: flex-start;

        flex-direction: column;
    }

    .signal {

        width: 100%;
    }

    .grid {

        grid-template-columns:
            1fr 1fr;

        gap: 10px;
    }

    .search-box {

        gap: 8px;
    }

    .search-btn {

        padding: 0 15px;
    }

    .price {

        font-size: 27px;
    }

    .stock-name {

        font-size: 22px;
    }

    .metric-grid {

        grid-template-columns:
            1fr 1fr;
    }

    .panel {

        padding: 17px;
    }

    #chart {

        height: 230px;
    }

    .actions .btn {

        padding:
            9px 11px;

        font-size: 12px;
    }
}

@media (max-width: 420px) {

    .grid {

        grid-template-columns: 1fr;
    }

    .search-box {

        flex-direction: column;
    }

    .search-btn {

        height: 48px;
    }

    .confidence-labels {

        font-size: 10px;
    }
}

</style>
</head>


<body>

<div class="page">


<header class="topbar">

    <div class="brand">

        <div class="logo">
            IE
        </div>

        <div>

            <div class="brand-title">
                InvestEdge
            </div>

            <div class="brand-sub">
                AI MARKET INTELLIGENCE
            </div>

        </div>

    </div>


    <div class="actions">

        <button
            class="btn"
            onclick="goDashboard()"
        >
            ← Dashboard
        </button>

    </div>

</header>


<main class="container">


    <!-- SEARCH -->

    <div class="search-box">

        <input
            id="symbolInput"
            placeholder="Search stock symbol — RELIANCE, TCS, INFY..."
            onkeydown="if(event.key==='Enter') loadResearch()"
        >

        <button
            class="search-btn"
            onclick="loadResearch()"
        >
            Analyse
        </button>

    </div>


    <div id="content">

        <div class="loading">
            Loading stock research...
        </div>

    </div>


</main>

</div>


<script>


/* =========================================================
   INITIAL STATE
   ========================================================= */

const params =
    new URLSearchParams(
        window.location.search
    );

let symbol =
    (
        params.get("symbol") ||
        "RELIANCE"
    ).toUpperCase();

document.getElementById(
    "symbolInput"
).value = symbol;


/* =========================================================
   NAVIGATION
   ========================================================= */

function goDashboard() {

    window.location.href =
        "/dashboard";
}


/* =========================================================
   ESCAPE HTML
   ========================================================= */

function esc(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   NUMBER FORMAT
   ========================================================= */

function number(
    value,
    decimals = 2
) {

    const n =
        Number(value);

    if (!Number.isFinite(n)) {

        return "—";
    }

    return n.toLocaleString(
        "en-IN",
        {
            minimumFractionDigits:
                decimals,

            maximumFractionDigits:
                decimals
        }
    );
}


/* =========================================================
   SIGNAL CLASS
   ========================================================= */

function signalClass(value) {

    const text =
        String(value || "")
            .toLowerCase();

    if (
        text.includes("positive") ||
        text.includes("bullish") ||
        text.includes("buy") ||
        text.includes("aligned")
    ) {

        return "green";
    }

    if (
        text.includes("negative") ||
        text.includes("bearish") ||
        text.includes("sell")
    ) {

        return "red";
    }

    return "yellow";
}


/* =========================================================
   BUY / HOLD / SELL
   ========================================================= */

function recommendation(
    score,
    unified,
    technical,
    market
) {

    const s =
        Number(score || 0);

    const signal =
        String(unified || "")
            .toLowerCase();

    const tech =
        String(technical || "")
            .toLowerCase();

    const marketDir =
        String(market || "")
            .toLowerCase();

    const rsi =
        Number(
            window.__researchTechnical?.rsi_14 ||
            0
        );


    /*
     * Strong positive conditions.
     */

    if (
        s >= 75 &&
        signal.includes("positive") &&
        marketDir.includes("positive") &&
        tech.includes("positive")
    ) {

        /*
         * RSI >= 70 means overbought.
         * Do not blindly call BUY.
         */

        if (rsi >= 70) {

            return [
                "HOLD",
                "yellow"
            ];
        }

        return [
            "BUY",
            "green"
        ];
    }


    /*
     * Strong negative conditions.
     */

    if (
        s <= 40 &&
        signal.includes("negative") &&
        marketDir.includes("negative")
    ) {

        return [
            "SELL",
            "red"
        ];
    }


    /*
     * Mixed conditions.
     */

    return [
        "HOLD",
        "yellow"
    ];
}


/* =========================================================
   CONFIDENCE
   ========================================================= */

function calculateConfidence(
    score,
    aiScore,
    unifiedSignal
) {

    const researchScore =
        Number(score || 0);

    const ai =
        Number(
            aiScore ||
            researchScore
        );

    const base =
        (
            researchScore * 0.65
        ) +
        (
            ai * 0.35
        );

    const signal =
        String(
            unifiedSignal || ""
        ).toLowerCase();

    let confidence =
        base;


    if (
        signal.includes("positive")
    ) {

        confidence += 5;
    }

    if (
        signal.includes("negative")
    ) {

        confidence -= 5;
    }


    return Math.max(
        0,
        Math.min(
            99,
            Math.round(
                confidence
            )
        )
    );
}


/* =========================================================
   PRICE LEVELS
   ========================================================= */

function calculateLevels(
    price,
    technical,
    history
) {

    const current =
        Number(price || 0);

    const volatility =
        Number(
            technical.volatility ||
            1
        );


    if (!current) {

        return {

            entryLow: 0,
            entryHigh: 0,
            target: 0,
            stopLoss: 0,
            support: 0,
            resistance: 0,
            riskReward: 0
        };
    }


    /*
     * Research reference levels.
     */

    const entryLow =
        current *
        (
            1 -
            Math.max(
                0.005,
                volatility / 100
            )
        );


    const entryHigh =
        current *
        (
            1 +
            0.0025
        );


    const targetDistance =
        Math.max(
            0.04,
            (
                volatility * 2
            ) / 100
        );


    const stopDistance =
        Math.max(
            0.025,
            (
                volatility * 1.5
            ) / 100
        );


    const target =
        current *
        (
            1 +
            targetDistance
        );


    const stopLoss =
        current *
        (
            1 -
            stopDistance
        );


    const closes =
        (
            history || []
        )
        .map(
            item =>
                Number(item.close)
        )
        .filter(
            Number.isFinite
        );


    const recent =
        closes.slice(-20);


    const support =
        recent.length
            ? Math.min(...recent)
            : current * 0.95;


    const resistance =
        recent.length
            ? Math.max(...recent)
            : current * 1.05;


    const reward =
        Math.max(
            target - current,
            0
        );


    const risk =
        Math.max(
            current - stopLoss,
            0.01
        );


    const riskReward =
        reward / risk;


    return {

        entryLow,
        entryHigh,
        target,
        stopLoss,
        support,
        resistance,
        riskReward
    };
}


/* =========================================================
   HISTORICAL CHART
   ========================================================= */

function renderChart(history) {

    const svg =
        document.getElementById(
            "chart"
        );


    if (
        !history ||
        history.length < 2
    ) {

        svg.innerHTML =
            `
            <text
                x="50%"
                y="50%"
                text-anchor="middle"
                fill="#71839a"
            >
                Historical chart unavailable
            </text>
            `;

        return;
    }


    const closes =
        history
            .map(
                x =>
                    Number(x.close)
            )
            .filter(
                Number.isFinite
            );


    if (
        closes.length < 2
    ) {

        svg.innerHTML =
            `
            <text
                x="50%"
                y="50%"
                text-anchor="middle"
                fill="#71839a"
            >
                Historical chart unavailable
            </text>
            `;

        return;
    }


    const width =
        1000;

    const height =
        300;

    const pad =
        30;


    const min =
        Math.min(...closes);

    const max =
        Math.max(...closes);

    const range =
        Math.max(
            max - min,
            1
        );


    const points =
        closes
            .map(
                (
                    price,
                    index
                ) => {

                    const x =
                        pad +
                        (
                            index /
                            (
                                closes.length - 1
                            )
                        ) *
                        (
                            width -
                            pad * 2
                        );


                    const y =
                        height -
                        pad -
                        (
                            (
                                price -
                                min
                            ) /
                            range
                        ) *
                        (
                            height -
                            pad * 2
                        );


                    return `${x},${y}`;
                }
            )
            .join(" ");


    svg.innerHTML = `

        <polyline
            points="${points}"
            fill="none"
            stroke="#22c55e"
            stroke-width="4"
            stroke-linecap="round"
            stroke-linejoin="round"
        />

        <text
            x="${pad}"
            y="24"
            fill="#7f91a8"
            font-size="12"
        >
            ₹${number(max)}
        </text>

        <text
            x="${pad}"
            y="${height - 8}"
            fill="#7f91a8"
            font-size="12"
        >
            ₹${number(min)}
        </text>

    `;
}


/* =========================================================
   MAIN RENDER
   ========================================================= */

function render(data) {


    if (data.error) {

        document.getElementById(
            "content"
        ).innerHTML =
            `
            <div class="error">
                ${esc(data.error)}
            </div>
            `;

        return;
    }


    const market =
        data.market_data || {};


    const marketAnalysis =
        data.market_analysis || {};


    const technical =
        data.technical_analysis || {};


    const fundamentals =
        data.fundamentals || {};


    const risk =
        data.risk_analysis ||
        data.risk ||
        {};


    const sentiment =
        data.news_sentiment || {};


    const reconciliation =
        data.signal_reconciliation ||
        marketAnalysis.signal_reconciliation ||
        {};


    const marketSignal =
        marketAnalysis.market_signal ||
        reconciliation.market_signal ||
        marketAnalysis.trend ||
        "—";


    const technicalSignal =
        marketAnalysis.technical_signal ||
        reconciliation.technical_signal ||
        technical.trend ||
        "—";


    const unifiedSignal =
        data.unified_signal ||
        marketAnalysis.unified_signal ||
        reconciliation.unified_signal ||
        "—";


    const breakdown =
        data.score_breakdown ||
        {};


    const news =
        data.news ||
        [];


    const score =
        Number(
            data.score || 0
        );


    const aiScore =
        Number(
            data.ai_score || 0
        );


    /*
     * Store technical data globally
     * for recommendation().
     */

    window.__researchTechnical =
        technical;


    const [
        rec,
        recClass
    ] =
        recommendation(
            score,
            unifiedSignal,
            technicalSignal,
            marketSignal
        );


    const confidence =
        calculateConfidence(
            score,
            aiScore,
            unifiedSignal
        );


    const levels =
        calculateLevels(
            market.price,
            technical,
            data.historical_data ||
            []
        );


    /* =====================================================
       BULLISH / BEARISH FACTORS
       ===================================================== */

    const bullishFactors =
        [];

    const bearishFactors =
        [];


    if (
        String(marketSignal)
            .toLowerCase()
            .includes("positive")
    ) {

        bullishFactors.push(
            "Market momentum"
        );

    } else {

        bearishFactors.push(
            "Market direction"
        );
    }


    if (
        String(technicalSignal)
            .toLowerCase()
            .includes("positive")
    ) {

        bullishFactors.push(
            "Technical trend"
        );

    } else {

        bearishFactors.push(
            "Technical trend"
        );
    }


    if (
        Number(
            breakdown.fundamental?.score ||
            0
        ) >= 60
    ) {

        bullishFactors.push(
            "Fundamentals"
        );

    } else {

        bearishFactors.push(
            "Fundamentals"
        );
    }


    if (
        String(
            sentiment.sentiment ||
            ""
        )
        .toLowerCase()
        .includes("positive")
    ) {

        bullishFactors.push(
            "News sentiment"
        );
    }


    if (
        String(
            sentiment.sentiment ||
            ""
        )
        .toLowerCase()
        .includes("negative")
    ) {

        bearishFactors.push(
            "News sentiment"
        );
    }


    /*
     * RSI interpretation.
     */

    const rsi =
        Number(
            technical.rsi_14 ||
            0
        );


    let rsiStatus =
        "Neutral";


    if (rsi >= 70) {

        rsiStatus =
            "Overbought";

    } else if (rsi <= 30) {

        rsiStatus =
            "Oversold";

    } else if (rsi >= 55) {

        rsiStatus =
            "Bullish";

    } else if (rsi <= 45) {

        rsiStatus =
            "Bearish";
    }


    /*
     * Data source.
     */

    const dataSource =
        technical.data_source ||
        "Upstox";


    const live =
        String(dataSource)
            .toLowerCase()
            .includes("upstox");


    /*
     * AI insight.
     */

    let aiInsight =
        data.ai_reasoning ||
        "AI reasoning is not available.";


    if (rsi >= 70) {

        aiInsight +=
            " RSI is above 70, indicating an overbought condition. "
            +
            "Momentum remains positive, but chasing the price may increase short-term risk.";
    }


    /* =====================================================
       RENDER
       ===================================================== */

    document.getElementById(
        "content"
    ).innerHTML = `


        <!-- HERO -->

        <section class="hero-card">

            <div class="stock-head">

                <div>

                    <div class="stock-name">

                        ${esc(
                            fundamentals.company_name ||
                            data.symbol
                        )}

                    </div>


                    <div class="stock-symbol">

                        NSE •
                        ${esc(data.symbol)}

                        •

                        ${esc(
                            fundamentals.sector ||
                            "Equity"
                        )}

                    </div>


                    <div class="price">

                        ₹${number(
                            market.price
                        )}


                        <span class="change ${
                            Number(
                                market.change_percent
                            ) >= 0
                                ? "positive"
                                : "negative"
                        }">

                            ${
                                Number(
                                    market.change_percent
                                ) >= 0
                                    ? "▲"
                                    : "▼"
                            }

                            ${number(
                                market.change_percent
                            )}%

                        </span>

                    </div>


                    ${
                        live
                            ? `
                                <div class="live-status">

                                    <span class="live-dot"></span>

                                    LIVE UPSTOX MARKET DATA

                                </div>
                              `
                            : `
                                <div class="live-status">

                                    <span class="live-dot"></span>

                                    ${esc(
                                        dataSource
                                    )}

                                </div>
                              `
                    }

                </div>


                <div class="signal">

                    <div class="signal-label">

                        INVESTEDGE SIGNAL

                    </div>


                    <div
                        class="signal-value"
                        style="color:${
                            recClass === "green"
                                ? "#4ade80"
                                : recClass === "red"
                                    ? "#fb7185"
                                    : "#fbbf24"
                        }"
                    >

                        ${rec}

                    </div>


                    <div class="score">

                        Research Score:

                        <strong>
                            ${number(score)}
                        </strong>

                    </div>


                    <div class="score">

                        AI Score:

                        <strong>
                            ${number(aiScore)}
                        </strong>

                    </div>


                    <div class="score">

                        Confidence:

                        <strong>
                            ${confidence}%
                        </strong>

                    </div>

                </div>

            </div>

        </section>


        <!-- CONFIDENCE -->

        <section class="panel confidence-panel">

            <h2>
                InvestEdge Confidence
            </h2>


            <div class="confidence-track">

                <div
                    class="confidence-fill"
                    style="width:${confidence}%"
                ></div>

            </div>


            <div class="confidence-labels">

                <span>
                    Low confidence
                </span>

                <strong
                    style="color:#4ade80;"
                >
                    ${confidence}%
                    confidence
                </strong>

                <span>
                    High confidence
                </span>

            </div>

        </section>


        <!-- SIGNAL CARDS -->

        <section class="grid">


            <div class="card">

                <div class="card-title">
                    MARKET SIGNAL
                </div>

                <div class="card-value">
                    ${esc(marketSignal)}
                </div>

                <div class="card-small">

                    Momentum

                    ${number(
                        marketAnalysis.momentum_score,
                        0
                    )}

                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    TECHNICAL
                </div>

                <div class="card-value">
                    ${esc(technicalSignal)}
                </div>

                <div class="card-small">

                    RSI
                    ${number(rsi,1)}

                    •
                    ${rsiStatus}

                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    FUNDAMENTALS
                </div>

                <div class="card-value">

                    ${number(
                        breakdown.fundamental?.score
                    )}

                </div>

                <div class="card-small">

                    P/E
                    ${number(
                        fundamentals.pe
                    )}

                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    RISK
                </div>

                <div class="card-value">

                    ${esc(
                        risk.risk_level ||
                        "—"
                    )}

                </div>

                <div class="card-small">

                    Risk score

                    ${number(
                        risk.risk_score,
                        0
                    )}

                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    SENTIMENT
                </div>

                <div class="card-value">

                    ${esc(
                        sentiment.sentiment ||
                        "—"
                    )}

                </div>

                <div class="card-small">

                    ${number(
                        sentiment.articles_analyzed,
                        0
                    )}

                    articles

                </div>

            </div>

        </section>


        <!-- BULLISH / BEARISH -->

        <section class="section-grid">


            <div class="panel">

                <h2>
                    Bullish Factors
                </h2>


                ${
                    bullishFactors.length

                        ? bullishFactors
                            .map(
                                item => `

                                    <div class="signal-row">

                                        <span>
                                            ▲
                                            ${esc(item)}
                                        </span>

                                        <span class="badge green">
                                            BULLISH
                                        </span>

                                    </div>

                                `
                            )
                            .join("")

                        : `
                            <div class="card-small">
                                No strong bullish factor detected.
                            </div>
                        `
                }

            </div>


            <div class="panel">

                <h2>
                    Bearish / Risk Factors
                </h2>


                ${
                    bearishFactors.length

                        ? bearishFactors
                            .map(
                                item => `

                                    <div class="signal-row">

                                        <span>
                                            ▼
                                            ${esc(item)}
                                        </span>

                                        <span class="badge red">
                                            CAUTION
                                        </span>

                                    </div>

                                `
                            )
                            .join("")

                        : `
                            <div class="card-small">
                                No major bearish factor detected.
                            </div>
                        `
                }


                ${
                    rsi >= 70

                        ? `

                            <div class="signal-row">

                                <span>
                                    RSI overbought
                                </span>

                                <span class="badge yellow">
                                    CAUTION
                                </span>

                            </div>

                          `

                        : ""
                }

            </div>

        </section>


        <!-- PRICE LEVELS -->

        <section class="panel">

            <h2>
                Research Price Levels
            </h2>


            <div class="metric-grid">


                <div class="metric">

                    <span>
                        Entry Zone
                    </span>

                    <strong>

                        ₹${number(
                            levels.entryLow
                        )}

                        –

                        ₹${number(
                            levels.entryHigh
                        )}

                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Target
                    </span>

                    <strong>

                        ₹${number(
                            levels.target
                        )}

                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Stop Loss
                    </span>

                    <strong>

                        ₹${number(
                            levels.stopLoss
                        )}

                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Support
                    </span>

                    <strong>

                        ₹${number(
                            levels.support
                        )}

                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Resistance
                    </span>

                    <strong>

                        ₹${number(
                            levels.resistance
                        )}

                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Risk / Reward
                    </span>

                    <strong>

                        1 :
                        ${number(
                            levels.riskReward
                        )}

                    </strong>

                </div>

            </div>


            <div
                class="card-small"
                style="margin-top:14px;"
            >

                These levels are algorithmic
                research references derived from
                current price, volatility and recent
                price history. They are not guaranteed
                predictions.

            </div>

        </section>


        <!-- SIGNAL INTELLIGENCE -->

        <section class="section-grid">


            <div class="panel">

                <h2>
                    Signal Intelligence
                </h2>


                <div class="signal-row">

                    <span>
                        Market Direction
                    </span>

                    <span
                        class="badge ${
                            signalClass(
                                marketSignal
                            )
                        }"
                    >

                        ${esc(
                            marketSignal
                        )}

                    </span>

                </div>


                <div class="signal-row">

                    <span>
                        Technical Direction
                    </span>

                    <span
                        class="badge ${
                            signalClass(
                                technicalSignal
                            )
                        }"
                    >

                        ${esc(
                            technicalSignal
                        )}

                    </span>

                </div>


                <div class="signal-row">

                    <span>
                        Unified Signal
                    </span>

                    <span
                        class="badge ${
                            signalClass(
                                unifiedSignal
                            )
                        }"
                    >

                        ${esc(
                            unifiedSignal
                        )}

                    </span>

                </div>


                <div class="signal-row">

                    <span>
                        Signal Consistency
                    </span>

                    <span
                        class="badge ${
                            signalClass(
                                reconciliation.signal_consistency
                            )
                        }"
                    >

                        ${esc(
                            reconciliation.signal_consistency ||
                            "—"
                        )}

                    </span>

                </div>

            </div>


            <!-- TECHNICAL -->

            <div class="panel">

                <h2>
                    Technical Indicators
                </h2>


                <div class="metric-grid">


                    <div class="metric">

                        <span>
                            RSI 14
                        </span>

                        <strong>
                            ${number(
                                rsi,
                                1
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            RSI Status
                        </span>

                        <strong>
                            ${esc(
                                rsiStatus
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            SMA 20
                        </span>

                        <strong>

                            ₹${number(
                                technical.sma_20
                            )}

                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            EMA 20
                        </span>

                        <strong>

                            ₹${number(
                                technical.ema_20
                            )}

                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Volatility
                        </span>

                        <strong>

                            ${number(
                                technical.volatility
                            )}%

                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Data Points
                        </span>

                        <strong>

                            ${number(
                                technical.data_points,
                                0
                            )}

                        </strong>

                    </div>

                </div>

            </div>

        </section>


        <!-- CHART -->

        <section class="panel chart-panel">

            <h2>
                Historical Price
            </h2>

            <svg
                id="chart"
                viewBox="0 0 1000 300"
                preserveAspectRatio="none"
            ></svg>

        </section>


        <!-- FUNDAMENTALS -->

        <section class="section-grid">


            <div class="panel">

                <h2>
                    Fundamental Snapshot
                </h2>


                <div class="metric-grid">


                    <div class="metric">

                        <span>
                            P/E
                        </span>

                        <strong>
                            ${number(
                                fundamentals.pe
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            P/B
                        </span>

                        <strong>
                            ${number(
                                fundamentals.pb
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            ROE
                        </span>

                        <strong>
                            ${number(
                                fundamentals.roe
                            )}%
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            ROCE
                        </span>

                        <strong>
                            ${number(
                                fundamentals.roce
                            )}%
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            ROA
                        </span>

                        <strong>
                            ${number(
                                fundamentals.roa
                            )}%
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            EV / EBITDA
                        </span>

                        <strong>
                            ${number(
                                fundamentals.ev_ebitda
                            )}
                        </strong>

                    </div>

                </div>

            </div>


            <!-- SCORE BREAKDOWN -->

            <div class="panel">

                <h2>
                    Score Breakdown
                </h2>


                <div class="signal-row">

                    <span>
                        Market
                    </span>

                    <strong>

                        ${number(
                            breakdown.market?.score
                        )}

                    </strong>

                </div>


                <div class="signal-row">

                    <span>
                        Technical
                    </span>

                    <strong>

                        ${number(
                            breakdown.technical?.score
                        )}

                    </strong>

                </div>


                <div class="signal-row">

                    <span>
                        Fundamental
                    </span>

                    <strong>

                        ${number(
                            breakdown.fundamental?.score
                        )}

                    </strong>

                </div>


                <div class="signal-row">

                    <span>
                        Risk
                    </span>

                    <strong>

                        ${number(
                            breakdown.risk?.score
                        )}

                    </strong>

                </div>


                <div class="signal-row">

                    <span>
                        News
                    </span>

                    <strong>

                        ${number(
                            breakdown.news?.score
                        )}

                    </strong>

                </div>

            </div>

        </section>


        <!-- AI -->

        <section class="panel ai">

            <h2 class="ai-title">

                ✦

                AI Research Insight

            </h2>


            <div>

                ${esc(
                    aiInsight
                )}

            </div>

        </section>


        <!-- NEWS -->

        <section
            class="panel"
            style="margin-top:18px;"
        >

            <h2>
                Market News
            </h2>


            ${
                news.length

                    ? news
                        .map(
                            item => `

                                <div class="news-item">

                                    <div class="news-title">

                                        ${esc(
                                            item.headline
                                        )}

                                    </div>

                                    <div class="news-meta">

                                        ${esc(
                                            item.published_time ||
                                            ""
                                        )}

                                        ${
                                            item.summary
                                                ? " • " +
                                                  esc(
                                                      item.summary
                                                  )
                                                : ""
                                        }

                                    </div>

                                </div>

                            `
                        )
                        .join("")

                    : `
                        <div class="card-small">

                            No news available.

                        </div>
                      `
            }

        </section>


        <!-- DATA STATUS -->

        <div class="disclaimer">

            <strong>
                Data status:
            </strong>

            ${
                live

                    ? `
                        Live market, historical,
                        fundamentals and news data are
                        currently being supplied through
                        the configured
                        <strong>Upstox provider</strong>.
                      `

                    : `
                        Current data source:
                        ${esc(dataSource)}.
                      `
            }

            BUY/HOLD/SELL is an algorithmic
            research signal and is not personalized
            financial advice.

        </div>

    `;


    renderChart(
        data.historical_data ||
        []
    );
}


/* =========================================================
   LOAD RESEARCH
   ========================================================= */

async function loadResearch() {

    const input =
        document.getElementById(
            "symbolInput"
        );


    const value =
        input.value
            .trim()
            .toUpperCase();


    if (!value) {

        return;
    }


    symbol =
        value;


    document.getElementById(
        "content"
    ).innerHTML =

        `
        <div class="loading">
            Analysing ${esc(symbol)}...
        </div>
        `;


    history.replaceState(
        null,
        "",
        "/research-ui?symbol=" +
        encodeURIComponent(
            symbol
        )
    );


    try {

        const response =
            await fetch(
                "/research?symbol=" +
                encodeURIComponent(
                    symbol
                )
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        render(data);


    } catch (error) {

        console.error(
            "Research loading error:",
            error
        );


        document.getElementById(
            "content"
        ).innerHTML =

            `
            <div class="error">

                Unable to load research.

                <br><br>

                Make sure the InvestEdge
                server is running.

            </div>
            `;
    }
}


/* =========================================================
   INITIAL LOAD
   ========================================================= */

loadResearch();

</script>

</body>
</html>
"""
    )