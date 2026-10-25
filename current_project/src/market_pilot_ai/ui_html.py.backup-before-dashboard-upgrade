def get_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvestEdge — AI Market Intelligence</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Inter, Segoe UI, Arial, sans-serif;
            background: #f7f4ec;
            color: #172033;
        }

        button {
            font-family: inherit;
        }

        .app {
            display: flex;
            min-height: 100vh;
        }

        /* SIDEBAR */

        .sidebar {
            width: 220px;
            background: #fffdf8;
            border-right: 1px solid #e8e2d6;
            padding: 22px 14px;
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            overflow-y: auto;
            z-index: 20;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 10px 26px;
        }

        .brand-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, #d99b22, #f0c35c);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 21px;
            font-weight: 800;
            box-shadow: 0 5px 14px rgba(200,145,30,.2);
        }

        .brand-name {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.7px;
        }

        .brand-sub {
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
            color: #777;
            margin-top: 2px;
        }

        .nav-title {
            font-size: 10px;
            font-weight: 800;
            color: #9b927f;
            letter-spacing: 1.2px;
            padding: 12px 12px 7px;
            text-transform: uppercase;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 11px 12px;
            margin: 3px 0;
            border-radius: 10px;
            font-size: 14px;
            color: #303642;
            cursor: pointer;
            transition: .2s;
        }

        .nav-item:hover {
            background: #f3eee3;
        }

        .nav-item.active {
            background: #eee5d3;
            font-weight: 700;
        }

        .nav-icon {
            width: 21px;
            text-align: center;
            font-size: 18px;
        }

        /* MAIN */

        .main {
            margin-left: 220px;
            width: calc(100% - 220px);
            padding: 15px 20px 40px;
        }

        /* TOPBAR */

        .topbar {
            display: grid;
            grid-template-columns: minmax(300px, 1fr) auto auto;
            gap: 20px;
            align-items: center;
            margin-bottom: 14px;
        }

        .search {
            height: 43px;
            background: white;
            border: 1px solid #e5dfd3;
            border-radius: 24px;
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 0 17px;
            color: #777;
            box-shadow: 0 3px 12px rgba(50,40,20,.03);
        }

        .search input {
            width: 100%;
            border: 0;
            outline: 0;
            font-size: 14px;
            background: transparent;
        }

        .indices {
            display: flex;
            gap: 28px;
        }

        .index {
            min-width: 100px;
        }

        .index-name {
            font-size: 11px;
            font-weight: 700;
            color: #4e5360;
        }

        .index-row {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-top: 2px;
        }

        .index-value {
            font-size: 15px;
            font-weight: 800;
        }

        .positive {
            color: #12975e;
        }

        .negative {
            color: #e04e52;
        }

        .profile {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #172033;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        /* HERO */

        .hero {
            min-height: 175px;
            border: 1px solid #e8dfce;
            border-radius: 18px;
            background:
                radial-gradient(circle at 72% 50%, rgba(227,182,82,.25), transparent 28%),
                linear-gradient(100deg, #fffdf7, #f6edda);
            padding: 27px 30px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 5px 18px rgba(40,30,10,.035);
        }

        .hero-copy {
            position: relative;
            z-index: 2;
        }

        .hero-kicker {
            color: #a47a25;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.6px;
            margin-bottom: 8px;
        }

        .hero h1 {
            font-size: 29px;
            margin: 0 0 7px;
            letter-spacing: -1px;
        }

        .hero p {
            margin: 0;
            color: #6c6b67;
            font-size: 14px;
        }

        .hero-art {
            position: absolute;
            right: 18%;
            bottom: -16px;
            font-size: 112px;
            opacity: .95;
            filter: drop-shadow(0 12px 12px rgba(120,90,20,.14));
        }

        .hero-bars {
            position: absolute;
            right: 7%;
            bottom: 0;
            display: flex;
            align-items: end;
            gap: 7px;
            opacity: .65;
        }

        .hero-bars span {
            width: 13px;
            background: linear-gradient(#dca92d,#f1cf77);
            border-radius: 5px 5px 0 0;
        }

        .hero-bars span:nth-child(1){height:32px}
        .hero-bars span:nth-child(2){height:51px}
        .hero-bars span:nth-child(3){height:72px}
        .hero-bars span:nth-child(4){height:94px}
        .hero-bars span:nth-child(5){height:115px}

        .hero-message {
            position: relative;
            z-index: 2;
            width: 190px;
            color: #42423e;
            font-size: 13px;
            line-height: 1.45;
            margin-right: 22px;
        }

        .hero-message strong {
            display: block;
            font-size: 14px;
            margin-bottom: 4px;
        }

        /* CARDS */

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 12px;
        }

        .feature {
            min-height: 142px;
            background: white;
            border: 1px solid #e7e0d3;
            border-radius: 15px;
            padding: 15px;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            transition: transform .2s, box-shadow .2s;
        }

        .feature:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(50,40,20,.09);
        }

        .feature-head {
            display: flex;
            gap: 11px;
            align-items: center;
        }

        .feature-icon {
            width: 43px;
            height: 43px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 21px;
            flex-shrink: 0;
        }

        .green { background: linear-gradient(135deg,#0fa56a,#35c98c); }
        .blue { background: linear-gradient(135deg,#2779e6,#66a9ff); }
        .purple { background: linear-gradient(135deg,#7544df,#a982ff); }
        .gold { background: linear-gradient(135deg,#d08d17,#efc04c); }
        .orange { background: linear-gradient(135deg,#ed751a,#f4a03c); }
        .red { background: linear-gradient(135deg,#e94242,#ff7777); }
        .teal { background: linear-gradient(135deg,#159a9c,#45c9c4); }

        .feature h3 {
            margin: 0;
            font-size: 17px;
        }

        .feature small {
            color: #767676;
            font-size: 10px;
        }

        .feature-value {
            position: absolute;
            left: 15px;
            bottom: 15px;
            font-size: 12px;
            color: #4b4b4b;
        }

        .feature-value strong {
            display: block;
            font-size: 15px;
            color: #172033;
            margin-top: 3px;
        }

        .feature-art {
            position: absolute;
            right: 7px;
            bottom: -5px;
            font-size: 67px;
            opacity: .18;
        }

        .arrow {
            position: absolute;
            right: 12px;
            bottom: 12px;
            width: 33px;
            height: 33px;
            border-radius: 50%;
            border: 1px solid #ddd6c9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            background: rgba(255,255,255,.85);
        }

        /* ANALYTICS */

        .analytics {
            display: grid;
            grid-template-columns: 1.25fr .95fr 1fr .9fr;
            gap: 10px;
            margin-top: 12px;
        }

        .panel {
            background: white;
            border: 1px solid #e7e0d3;
            border-radius: 15px;
            padding: 15px;
            min-height: 220px;
        }

        .panel-title {
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 11px;
        }

        .panel-sub {
            font-size: 10px;
            color: #888;
            margin-left: 5px;
        }

        .market-price {
            font-size: 25px;
            font-weight: 800;
        }

        .market-change {
            color: #12975e;
            font-size: 12px;
            font-weight: 700;
            margin-left: 5px;
        }

        .chart {
            height: 105px;
            margin-top: 13px;
            position: relative;
            overflow: hidden;
        }

        .chart svg {
            width: 100%;
            height: 100%;
        }

        .donut {
            width: 108px;
            height: 108px;
            border-radius: 50%;
            background: conic-gradient(
                #13aa6c 0 72%,
                #ef5350 72% 90%,
                #c9c9c9 90% 100%
            );
            margin: 12px auto;
            position: relative;
        }

        .donut:after {
            content: "72%";
            position: absolute;
            inset: 25px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 19px;
            font-weight: 800;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 10px;
            font-size: 10px;
        }

        .dot {
            width: 9px;
            height: 9px;
            display: inline-block;
            border-radius: 3px;
            margin-right: 3px;
        }

        .crypto-row {
            display: grid;
            grid-template-columns: 28px 1fr auto auto;
            align-items: center;
            gap: 6px;
            padding: 7px 0;
            border-bottom: 1px solid #f0ede7;
            font-size: 11px;
        }

        .coin {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #f4c44e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        .allocation {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
        }

        .allocation-donut {
            width: 112px;
            height: 112px;
            border-radius: 50%;
            background: conic-gradient(
                #315fae 0 35%,
                #1eaf72 35% 65%,
                #efa91d 65% 85%,
                #9175ca 85% 95%,
                #ef5b5b 95% 100%
            );
            position: relative;
            flex-shrink: 0;
        }

        .allocation-donut:after {
            content: "₹12.4L";
            position: absolute;
            inset: 29px;
            background: white;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 13px;
            font-weight: 800;
        }

        .allocation-list {
            font-size: 10px;
            line-height: 2;
        }

        /* LOWER */

        .lower {
            display: grid;
            grid-template-columns: 1fr 1fr 1.15fr .9fr;
            gap: 10px;
            margin-top: 12px;
        }

        .table-panel {
            background: white;
            border: 1px solid #e7e0d3;
            border-radius: 15px;
            padding: 13px;
        }

        .table-title {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 7px;
        }

        .view {
            font-size: 9px;
            color: #4b72a8;
            cursor: pointer;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
        }

        th {
            text-align: left;
            color: #929292;
            font-weight: 600;
            padding: 5px 2px;
        }

        td {
            padding: 7px 2px;
            border-top: 1px solid #f0ede8;
        }

        .news {
            display: flex;
            gap: 9px;
            padding: 7px 0;
            border-bottom: 1px solid #f0ede8;
        }

        .news-image {
            width: 42px;
            height: 34px;
            border-radius: 7px;
            background: linear-gradient(135deg,#d8c7a2,#f4ebd7);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
        }

        .news-title {
            font-size: 10px;
            line-height: 1.3;
            font-weight: 650;
        }

        .news-time {
            font-size: 8px;
            color: #999;
            margin-top: 3px;
        }

        .insight {
            display: flex;
            gap: 9px;
            padding: 8px 0;
            border-bottom: 1px solid #f0ede8;
        }

        .insight-icon {
            width: 31px;
            height: 31px;
            border-radius: 8px;
            background: #edf7ef;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
        }

        .insight strong {
            display: block;
            font-size: 10px;
        }

        .insight span {
            display: block;
            font-size: 9px;
            color: #777;
            line-height: 1.3;
            margin-top: 2px;
        }

        /* AUTH */

        .auth-buttons {
            position: fixed;
            right: 18px;
            top: 72px;
            z-index: 30;
        }

        .auth-btn {
            border: 1px solid #dfd5c3;
            background: #fffdf8;
            border-radius: 18px;
            padding: 7px 13px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 700;
        }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(20,25,35,.42);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }

        .modal.show {
            display: flex;
        }

        .modal-box {
            width: 390px;
            max-width: calc(100vw - 30px);
            background: #fffdf8;
            border-radius: 18px;
            padding: 26px;
            box-shadow: 0 25px 70px rgba(0,0,0,.2);
        }

        .modal-box h2 {
            margin: 0 0 6px;
        }

        .modal-box p {
            color: #777;
            font-size: 12px;
        }

        .modal-box input {
            width: 100%;
            height: 42px;
            margin: 7px 0;
            border: 1px solid #ded8cb;
            border-radius: 9px;
            padding: 0 12px;
            outline: 0;
        }

        .modal-submit {
            width: 100%;
            height: 43px;
            border: 0;
            border-radius: 9px;
            background: #172033;
            color: white;
            font-weight: 700;
            margin-top: 8px;
            cursor: pointer;
        }

        .close {
            float: right;
            cursor: pointer;
            font-size: 20px;
        }

        @media(max-width:1200px) {
            .feature-grid {
                grid-template-columns: repeat(3,1fr);
            }

            .analytics,
            .lower {
                grid-template-columns: repeat(2,1fr);
            }
        }

        @media(max-width:800px) {
            .sidebar {
                display:none;
            }

            .main {
                margin-left:0;
                width:100%;
                padding:10px;
            }

            .topbar {
                grid-template-columns:1fr;
            }

            .indices {
                overflow-x:auto;
            }

            .feature-grid {
                grid-template-columns:1fr 1fr;
            }

            .hero-art,
            .hero-message {
                display:none;
            }
        }
    </style>
</head>

<body>

<div class="app">

    <aside class="sidebar">

        <div class="brand">
            <div class="brand-icon">▥</div>
            <div>
                <div class="brand-name">InvestEdge</div>
                <div class="brand-sub">AI MARKET INTELLIGENCE</div>
            </div>
        </div>

        <div class="nav-item active">
            <span class="nav-icon">⌂</span> Dashboard
        </div>

        <div class="nav-item"><span class="nav-icon">▥</span> Stocks</div>
        <div class="nav-item"><span class="nav-icon">◉</span> Mutual Funds</div>
        <div class="nav-item"><span class="nav-icon">▣</span> SIP Planner</div>
        <div class="nav-item"><span class="nav-icon">♜</span> Bonds</div>
        <div class="nav-item"><span class="nav-icon">▥</span> ETFs</div>
        <div class="nav-item"><span class="nav-icon">₿</span> Crypto</div>
        <div class="nav-item"><span class="nav-icon">🚀</span> IPOs</div>
        <div class="nav-item"><span class="nav-icon">◔</span> Portfolio</div>
        <div class="nav-item"><span class="nav-icon">▤</span> Market News</div>
        <div class="nav-item"><span class="nav-icon">✦</span> AI Research</div>

        <div class="nav-title">Tools</div>

        <div class="nav-item"><span class="nav-icon">⌁</span> Stock Screener</div>
        <div class="nav-item"><span class="nav-icon">⇄</span> Comparisons</div>
        <div class="nav-item"><span class="nav-icon">▦</span> Calculators</div>
        <div class="nav-item"><span class="nav-icon">☆</span> Watchlist</div>
        <div class="nav-item"><span class="nav-icon">♧</span> Alerts</div>
        <div class="nav-item"><span class="nav-icon">⚙</span> Settings</div>

    </aside>

    <main class="main">

        <div class="topbar">

            <div class="search">
                <span>⌕</span>
                <input id="searchInput"
                       placeholder="Search any stock, mutual fund, crypto, bond, ETF, IPO..."
                       onkeydown="handleSearch(event)">
            </div>

            <div class="indices">

                <div class="index">
                    <div class="index-name">NIFTY 50</div>
                    <div class="index-row">
                        <span class="index-value">24,695.35</span>
                        <span class="positive">▲ +0.82%</span>
                    </div>
                </div>

                <div class="index">
                    <div class="index-name">SENSEX</div>
                    <div class="index-row">
                        <span class="index-value">80,914.82</span>
                        <span class="positive">▲ +0.78%</span>
                    </div>
                </div>

                <div class="index">
                    <div class="index-name">BANK NIFTY</div>
                    <div class="index-row">
                        <span class="index-value">55,208.40</span>
                        <span class="positive">▲ +1.12%</span>
                    </div>
                </div>

            </div>

            <div class="profile">K</div>

        </div>

        <!-- HERO -->

        <section class="hero">

            <div class="hero-copy">
                <div class="hero-kicker">AI-POWERED INVESTMENT RESEARCH</div>
                <h1>Hi Kshitij! 👋</h1>
                <h1 style="font-size:24px;margin-top:-3px;">
                    Track. Analyse. Invest Smarter.
                </h1>
                <p>Real market data • AI insights • One workspace</p>
            </div>

            <div class="hero-art">🐂</div>

            <div class="hero-bars">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>

            <div class="hero-message">
                <strong>Disciplined investing today,</strong>
                a wealthier tomorrow.
            </div>

        </section>

        <!-- FEATURES -->

        <section class="feature-grid">

            <div class="feature" onclick="openFeature('Stocks')">
                <div class="feature-head">
                    <div class="feature-icon green">▥</div>
                    <div>
                        <h3>Stocks</h3>
                        <small>Research • Analyse • Invest</small>
                    </div>
                </div>
                <div class="feature-value">
                    NIFTY 50
                    <strong>24,695.35 <span class="positive">+0.82%</span></strong>
                </div>
                <div class="feature-art">📈</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('Mutual Funds')">
                <div class="feature-head">
                    <div class="feature-icon blue">◉</div>
                    <div>
                        <h3>Mutual Funds</h3>
                        <small>Equity • Debt • Hybrid</small>
                    </div>
                </div>
                <div class="feature-value">
                    Total AUM (India)
                    <strong>₹54.8 Lakh Cr <span class="positive">+1.5%</span></strong>
                </div>
                <div class="feature-art">📊</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('SIP Planner')">
                <div class="feature-head">
                    <div class="feature-icon purple">▣</div>
                    <div>
                        <h3>SIP Planner</h3>
                        <small>Plan • Calculate • Grow</small>
                    </div>
                </div>
                <div class="feature-value">
                    Monthly Investment
                    <strong>₹10,000</strong>
                </div>
                <div class="feature-art">🌱</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('Bonds')">
                <div class="feature-head">
                    <div class="feature-icon gold">♜</div>
                    <div>
                        <h3>Bonds</h3>
                        <small>Government • Corporate</small>
                    </div>
                </div>
                <div class="feature-value">
                    Avg. Yield
                    <strong>7.14% <span class="positive">+0.05%</span></strong>
                </div>
                <div class="feature-art">🪙</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('ETFs')">
                <div class="feature-head">
                    <div class="feature-icon orange">▥</div>
                    <div>
                        <h3>ETFs</h3>
                        <small>Index • Gold • Sectoral</small>
                    </div>
                </div>
                <div class="feature-value">
                    Gold ETF
                    <strong>₹62.18 <span class="positive">+1.32%</span></strong>
                </div>
                <div class="feature-art">🪙</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('Crypto')">
                <div class="feature-head">
                    <div class="feature-icon red">₿</div>
                    <div>
                        <h3>Crypto</h3>
                        <small>Bitcoin • Ethereum • Others</small>
                    </div>
                </div>
                <div class="feature-value">
                    BTC
                    <strong>₹82,92,791 <span class="positive">+0.29%</span></strong>
                </div>
                <div class="feature-art">₿</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('IPOs')">
                <div class="feature-head">
                    <div class="feature-icon purple">🚀</div>
                    <div>
                        <h3>IPOs</h3>
                        <small>Upcoming • Analyse • Apply</small>
                    </div>
                </div>
                <div class="feature-value">
                    Upcoming IPOs
                    <strong>4 Open</strong>
                </div>
                <div class="feature-art">📈</div>
                <div class="arrow">→</div>
            </div>

            <div class="feature" onclick="openFeature('Portfolio')">
                <div class="feature-head">
                    <div class="feature-icon teal">◔</div>
                    <div>
                        <h3>Portfolio</h3>
                        <small>Track • Analyse • Optimize</small>
                    </div>
                </div>
                <div class="feature-value">
                    Total Value
                    <strong>₹12,40,521 <span class="positive">+12.4%</span></strong>
                </div>
                <div class="feature-art">◔</div>
                <div class="arrow">→</div>
            </div>

        </section>

        <!-- ANALYTICS -->

        <section class="analytics">

            <div class="panel">

                <div class="panel-title">
                    Market Pulse
                    <span class="panel-sub">NIFTY 50</span>
                </div>

                <div>
                    <span class="market-price">24,695.35</span>
                    <span class="market-change">▲ +202.40 (+0.82%)</span>
                </div>

                <div class="chart">
                    <svg viewBox="0 0 500 120" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#8edeb8" stop-opacity=".55"/>
                                <stop offset="100%" stop-color="#8edeb8" stop-opacity=".03"/>
                            </linearGradient>
                        </defs>
                        <path
                            d="M0,94 L35,78 L65,84 L95,60 L125,69 L155,57 L185,63 L215,53 L245,55 L275,48 L305,52 L335,39 L365,46 L395,28 L425,34 L455,19 L500,9 L500,120 L0,120 Z"
                            fill="url(#area)"
                        />
                        <polyline
                            points="0,94 35,78 65,84 95,60 125,69 155,57 185,63 215,53 245,55 275,48 305,52 335,39 365,46 395,28 425,34 455,19 500,9"
                            fill="none"
                            stroke="#16a66d"
                            stroke-width="3"
                        />
                    </svg>
                </div>

                <div style="display:flex;justify-content:space-between;font-size:9px;color:#999;">
                    <span>09:15</span>
                    <span>10:30</span>
                    <span>12:00</span>
                    <span>13:30</span>
                    <span>15:00</span>
                </div>

            </div>

            <div class="panel">

                <div class="panel-title">
                    Bullish vs Bearish
                    <span class="panel-sub">(NIFTY 500)</span>
                </div>

                <div class="donut"></div>

                <div class="legend">
                    <span><i class="dot" style="background:#13aa6c"></i>Bullish 72%</span>
                    <span><i class="dot" style="background:#ef5350"></i>Bearish 18%</span>
                    <span><i class="dot" style="background:#c9c9c9"></i>Neutral 10%</span>
                </div>

                <div style="font-size:11px;font-weight:700;margin-top:12px;">
                    Market Breadth
                </div>

                <div style="height:8px;border-radius:10px;background:linear-gradient(90deg,#16a66d 0 65%,#ef5350 65% 90%,#bbb 90%);margin-top:7px;"></div>

                <div style="display:flex;justify-content:space-between;font-size:9px;margin-top:5px;">
                    <span>Advancing <b class="positive">3,542</b></span>
                    <span>Declining <b class="negative">1,287</b></span>
                    <span>Unchanged <b>471</b></span>
                </div>

            </div>

            <div class="panel">

                <div class="panel-title">
                    Live Digital Assets
                    <span class="view">View All →</span>
                </div>

                <div class="crypto-row">
                    <div class="coin">₿</div>
                    <b>BTC</b>
                    <span>₹82,92,791</span>
                    <span class="positive">+0.29%</span>
                </div>

                <div class="crypto-row">
                    <div class="coin" style="background:#d7d7ff">Ξ</div>
                    <b>ETH</b>
                    <span>₹2,61,014</span>
                    <span class="negative">-0.30%</span>
                </div>

                <div class="crypto-row">
                    <div class="coin" style="background:#dedcff">S</div>
                    <b>SOL</b>
                    <span>₹11,520</span>
                    <span class="negative">-0.85%</span>
                </div>

                <div class="crypto-row">
                    <div class="coin" style="background:#f4d78d">B</div>
                    <b>BNB</b>
                    <span>₹75,482</span>
                    <span class="negative">-0.40%</span>
                </div>

                <div class="crypto-row">
                    <div class="coin" style="background:#ddd">X</div>
                    <b>XRP</b>
                    <span>₹145</span>
                    <span class="negative">-0.21%</span>
                </div>

            </div>

            <div class="panel">

                <div class="panel-title">
                    Portfolio Allocation
                    <span class="view">View Details →</span>
                </div>

                <div class="allocation">

                    <div class="allocation-donut"></div>

                    <div class="allocation-list">
                        <div>🔵 Equity <b>35%</b></div>
                        <div>🟢 Mutual Funds <b>30%</b></div>
                        <div>🟡 Gold / ETFs <b>20%</b></div>
                        <div>🟣 Bonds <b>10%</b></div>
                        <div>🔴 Crypto <b>5%</b></div>
                    </div>

                </div>

                <div style="display:flex;gap:8px;margin-top:15px;">
                    <div style="flex:1;background:#f1f7f2;border-radius:9px;padding:9px;">
                        <small>Overall P&L</small>
                        <strong class="positive" style="display:block;font-size:15px;">+12.4%</strong>
                    </div>

                    <div style="flex:1;background:#f1f7f2;border-radius:9px;padding:9px;">
                        <small>Today's P&L</small>
                        <strong class="positive" style="display:block;font-size:15px;">+0.8%</strong>
                    </div>
                </div>

            </div>

        </section>

        <!-- LOWER PANELS -->

        <section class="lower">

            <div class="table-panel">

                <div class="table-title">
                    <span>🟢 Top Gainers <small>(NIFTY 50)</small></span>
                    <span class="view">View All →</span>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Stock</th>
                            <th>Price</th>
                            <th>Change</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr><td>1</td><td>🟢 RELIANCE</td><td>₹2,845.60</td><td class="positive">+2.36%</td></tr>
                        <tr><td>2</td><td>🔵 HDFC BANK</td><td>₹1,642.25</td><td class="positive">+1.82%</td></tr>
                        <tr><td>3</td><td>🔷 TCS</td><td>₹3,958.10</td><td class="positive">+1.45%</td></tr>
                        <tr><td>4</td><td>🟣 INFY</td><td>₹1,512.70</td><td class="positive">+1.28%</td></tr>
                        <tr><td>5</td><td>🔴 ICICI BANK</td><td>₹1,099.45</td><td class="positive">+1.20%</td></tr>
                    </tbody>
                </table>

            </div>

            <div class="table-panel">

                <div class="table-title">
                    <span>🔴 Top Losers <small>(NIFTY 50)</small></span>
                    <span class="view">View All →</span>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Stock</th>
                            <th>Price</th>
                            <th>Change</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr><td>1</td><td>🔵 TATA STEEL</td><td>₹148.20</td><td class="negative">-1.24%</td></tr>
                        <tr><td>2</td><td>🟠 ONGC</td><td>₹252.40</td><td class="negative">-1.10%</td></tr>
                        <tr><td>3</td><td>🟣 ADANI PORTS</td><td>₹1,286.75</td><td class="negative">-0.95%</td></tr>
                        <tr><td>4</td><td>🟡 HINDALCO</td><td>₹423.10</td><td class="negative">-0.92%</td></tr>
                        <tr><td>5</td><td>🟢 BPCL</td><td>₹298.60</td><td class="negative">-0.86%</td></tr>
                    </tbody>
                </table>

            </div>

            <div class="table-panel">

                <div class="table-title">
                    <span>📰 Recent Market News</span>
                    <span class="view">View All →</span>
                </div>

                <div class="news">
                    <div class="news-image">🏦</div>
                    <div>
                        <div class="news-title">RBI keeps repo rate unchanged at 6.5%</div>
                        <div class="news-time">2 hours ago</div>
                    </div>
                </div>

                <div class="news">
                    <div class="news-image">🌱</div>
                    <div>
                        <div class="news-title">Reliance announces green energy expansion</div>
                        <div class="news-time">4 hours ago</div>
                    </div>
                </div>

                <div class="news">
                    <div class="news-image">🏛️</div>
                    <div>
                        <div class="news-title">SEBI proposes new norms for IPO disclosures</div>
                        <div class="news-time">6 hours ago</div>
                    </div>
                </div>

                <div class="news">
                    <div class="news-image">📈</div>
                    <div>
                        <div class="news-title">Indian markets end higher on global cues</div>
                        <div class="news-time">8 hours ago</div>
                    </div>
                </div>

            </div>

            <div class="table-panel">

                <div class="table-title">
                    <span>☀️ AI Insights</span>
                    <span style="background:#f1b51e;color:white;padding:3px 7px;border-radius:10px;font-size:8px;">NEW</span>
                </div>

                <div class="insight">
                    <div class="insight-icon">⬆️</div>
                    <div>
                        <strong>RELIANCE shows strong bullish momentum</strong>
                        <span>Supported by higher volumes and positive institutional buying.</span>
                    </div>
                </div>

                <div class="insight">
                    <div class="insight-icon">📊</div>
                    <div>
                        <strong>Consider SIP in Index Funds</strong>
                        <span>Current market conditions favour long-term wealth creation.</span>
                    </div>
                </div>

                <div class="insight">
                    <div class="insight-icon">🪙</div>
                    <div>
                        <strong>Gold ETFs gaining momentum</strong>
                        <span>Hedge against volatility with gold allocation.</span>
                    </div>
                </div>

            </div>

        </section>

    </main>
</div>

<!-- AUTH -->

<div class="auth-buttons">
    <button class="auth-btn" onclick="openLogin()">Login / Sign Up</button>
</div>

<div class="modal" id="authModal">
    <div class="modal-box auth-box">

        <span class="close" onclick="closeLogin()">×</span>

        <div class="auth-brand">
            <div class="auth-logo">IE</div>
            <div>
                <div class="auth-title">InvestEdge</div>
                <div class="auth-subtitle">AI Market Intelligence</div>
            </div>
        </div>

        <!-- SIGN IN -->
        <div id="loginPanel">

            <h2>Welcome back</h2>
            <p class="auth-description">
                Sign in to access your investment workspace.
            </p>

            <label>Email</label>
            <input id="authEmail" type="email" placeholder="you@example.com" autocomplete="email">

            <label>Password</label>
            <div class="password-wrap">
                <input id="authPassword" type="password" placeholder="Enter your password" autocomplete="current-password">
                <button type="button" class="password-toggle" onclick="togglePassword('authPassword', this)">Show</button>
            </div>

            <div class="auth-options">
                <label class="remember-label">
                    <input id="rememberMe" type="checkbox" checked>
                    <span>Remember me</span>
                </label>

                <button type="button" class="link-button" onclick="showForgotPassword()">
                    Forgot password?
                </button>
            </div>

            <button class="modal-submit auth-primary" onclick="loginUser()">
                Sign In
            </button>

            <p class="auth-switch">
                New to InvestEdge?
                <button type="button" class="link-button" onclick="showSignup()">
                    Create an account
                </button>
            </p>

        </div>

        <!-- SIGN UP -->
        <div id="signupPanel" style="display:none;">

            <h2>Create your account</h2>
            <p class="auth-description">
                Start your personalized investment workspace.
            </p>

            <label>Full name</label>
            <input id="signupName" type="text" placeholder="Your full name" autocomplete="name">

            <label>Email</label>
            <input id="signupEmail" type="email" placeholder="you@example.com" autocomplete="email">

            <label>Phone</label>
            <input id="signupPhone" type="tel" placeholder="+91 9876543210" autocomplete="tel">

            <label>Password</label>
            <div class="password-wrap">
                <input id="signupPassword" type="password" placeholder="Minimum 8 characters" autocomplete="new-password" oninput="updatePasswordStrength()">
                <button type="button" class="password-toggle" onclick="togglePassword('signupPassword', this)">Show</button>
            </div>

            <div id="passwordStrength" class="password-strength">
                Use 8+ characters with letters and numbers.
            </div>

            <button class="modal-submit auth-primary" onclick="signupUser()">
                Create Account
            </button>

            <p class="auth-switch">
                Already have an account?
                <button type="button" class="link-button" onclick="showLogin()">
                    Sign in
                </button>
            </p>

        </div>

        <!-- FORGOT PASSWORD -->
        <div id="forgotPanel" style="display:none;">

            <h2>Reset your password</h2>
            <p class="auth-description">
                Enter your email and we'll start the password recovery process.
            </p>

            <label>Email</label>
            <input id="forgotIdentifier" type="email" placeholder="you@example.com" autocomplete="email">

            <button class="modal-submit auth-primary" onclick="requestPasswordReset()">
                Send Reset OTP
            </button>

            <div id="otpPanel" style="display:none;margin-top:18px;">

                <label>OTP</label>
                <input id="resetOtp" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit OTP">

                <label>New password</label>
                <div class="password-wrap">
                    <input id="resetPassword" type="password" placeholder="Minimum 8 characters" autocomplete="new-password">
                    <button type="button" class="password-toggle" onclick="togglePassword('resetPassword', this)">Show</button>
                </div>

                <button class="modal-submit auth-primary" onclick="resetPassword()">
                    Set New Password
                </button>

            </div>

            <p class="auth-switch">
                Remember your password?
                <button type="button" class="link-button" onclick="showLogin()">
                    Back to sign in
                </button>
            </p>

        </div>

        <!-- ACCOUNT / CHANGE PASSWORD -->
        <div id="accountPanel" style="display:none;">

            <h2>Account security</h2>
            <p class="auth-description">
                Manage your InvestEdge account.
            </p>

            <label>Current password</label>
            <div class="password-wrap">
                <input id="currentPassword" type="password" placeholder="Current password">
                <button type="button" class="password-toggle" onclick="togglePassword('currentPassword', this)">Show</button>
            </div>

            <label>New password</label>
            <div class="password-wrap">
                <input id="newPassword" type="password" placeholder="New password">
                <button type="button" class="password-toggle" onclick="togglePassword('newPassword', this)">Show</button>
            </div>

            <button class="modal-submit auth-primary" onclick="changePassword()">
                Change Password
            </button>

            <button class="modal-submit auth-secondary" onclick="logoutUser()">
                Log Out
            </button>

        </div>

        <div id="authMessage" class="auth-message"></div>

    </div>
</div>

<script>

let currentUserIdentifier = "";

function openLogin() {
    document.getElementById("authModal").classList.add("show");
    showLogin();
}

function closeLogin() {
    document.getElementById("authModal").classList.remove("show");
}

function clearAuthMessage() {
    const box = document.getElementById("authMessage");
    box.textContent = "";
    box.className = "auth-message";
}

function showMessage(message, type="info") {
    const box = document.getElementById("authMessage");
    box.textContent = message;
    box.className = "auth-message " + type;
}

function hideAllAuthPanels() {
    document.getElementById("loginPanel").style.display = "none";
    document.getElementById("signupPanel").style.display = "none";
    document.getElementById("forgotPanel").style.display = "none";
    document.getElementById("accountPanel").style.display = "none";
    clearAuthMessage();
}

function showLogin() {
    hideAllAuthPanels();
    document.getElementById("loginPanel").style.display = "block";
}

function showSignup() {
    hideAllAuthPanels();
    document.getElementById("signupPanel").style.display = "block";
}

function showForgotPassword() {
    hideAllAuthPanels();
    document.getElementById("forgotPanel").style.display = "block";
}

function showAccount() {
    hideAllAuthPanels();
    document.getElementById("accountPanel").style.display = "block";
}

function togglePassword(id, button) {
    const input = document.getElementById(id);

    if (input.type === "password") {
        input.type = "text";
        button.textContent = "Hide";
    } else {
        input.type = "password";
        button.textContent = "Show";
    }
}

function updatePasswordStrength() {
    const password = document.getElementById("signupPassword").value;
    const box = document.getElementById("passwordStrength");

    if (password.length < 8) {
        box.textContent = "Weak — use at least 8 characters.";
        box.className = "password-strength weak";
        return;
    }

    if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
        box.textContent = "Good — add letters and numbers for a stronger password.";
        box.className = "password-strength medium";
        return;
    }

    box.textContent = "Strong password.";
    box.className = "password-strength strong";
}

async function loginUser() {

    const identifier = document.getElementById("authEmail").value.trim();
    const password = document.getElementById("authPassword").value;
    const rememberMe = document.getElementById("rememberMe").checked;

    if (!identifier || !password) {
        showMessage("Please enter your email and password.", "error");
        return;
    }

    try {

        const response = await fetch("/auth-v2/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                identifier: identifier,
                password: password,
                remember_me: rememberMe
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(
                typeof data.detail === "string"
                    ? data.detail
                    : "Login failed.",
                "error"
            );
            return;
        }

        currentUserIdentifier = identifier.toLowerCase();

        if (rememberMe) {
            localStorage.setItem("investedge_identifier", currentUserIdentifier);
            localStorage.setItem("investedge_token", data.access_token || "");
        } else {
            sessionStorage.setItem("investedge_identifier", currentUserIdentifier);
            sessionStorage.setItem("investedge_token", data.access_token || "");
        }

        showMessage("Login successful. Welcome to InvestEdge!", "success");

        setTimeout(() => {
            closeLogin();
        },2000);

    } catch (error) {
        showMessage("Authentication service is unavailable.", "error");
    }
}

async function signupUser() {

    const name = document.getElementById("signupName").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const phone = document.getElementById("signupPhone").value.trim();
    const password = document.getElementById("signupPassword").value;

    if (!name || !email || !phone || !password) {
        showMessage("Please complete all fields.", "error");
        return;
    }

    if (password.length < 8) {
        showMessage("Password must contain at least 8 characters.", "error");
        return;
    }

    try {

        const response = await fetch("/auth-v2/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                phone: phone,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(
                typeof data.detail === "string"
                    ? data.detail
                    : "Account creation failed.",
                "error"
            );
            return;
        }

        document.getElementById("authEmail").value = email;

        showLogin();

        showMessage(
            "Account created successfully. Please sign in.",
            "success"
        );

    } catch (error) {
        showMessage("Authentication service is unavailable.", "error");
    }
}

async function requestPasswordReset() {

    const identifier = document.getElementById("forgotIdentifier").value.trim();

    if (!identifier) {
        showMessage("Please enter your email address.", "error");
        return;
    }

    try {

        const response = await fetch("/auth-v2/forgot-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                identifier: identifier
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(
                typeof data.detail === "string"
                    ? data.detail
                    : "Unable to start password reset.",
                "error"
            );
            return;
        }

        document.getElementById("otpPanel").style.display = "block";

        let message = data.message || "If the account exists, an OTP has been sent.";

        if (data.otp || data.dev_otp) {
            message += " Development OTP: " + (data.otp || data.dev_otp);
        }

        showMessage(message, "success");

    } catch (error) {
        showMessage("Authentication service is unavailable.", "error");
    }
}

async function resetPassword() {

    const identifier = document.getElementById("forgotIdentifier").value.trim();
    const otp = document.getElementById("resetOtp").value.trim();
    const newPassword = document.getElementById("resetPassword").value;

    if (!identifier || !otp || !newPassword) {
        showMessage("Please complete the OTP and new password fields.", "error");
        return;
    }

    if (newPassword.length < 8) {
        showMessage("New password must contain at least 8 characters.", "error");
        return;
    }

    try {

        const response = await fetch("/auth-v2/reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                identifier: identifier,
                otp: otp,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(
                typeof data.detail === "string"
                    ? data.detail
                    : "Password reset failed.",
                "error"
            );
            return;
        }

        document.getElementById("authEmail").value = identifier;

        showLogin();

        showMessage(
            "Password reset successfully. Please sign in.",
            "success"
        );

    } catch (error) {
        showMessage("Authentication service is unavailable.", "error");
    }
}

async function changePassword() {

    if (!currentUserIdentifier) {
        showLogin();
        return;
    }

    const currentPassword = document.getElementById("currentPassword").value;
    const newPassword = document.getElementById("newPassword").value;

    if (!currentPassword || !newPassword) {
        showMessage("Please enter both passwords.", "error");
        return;
    }

    if (newPassword.length < 8) {
        showMessage("New password must contain at least 8 characters.", "error");
        return;
    }

    try {

        const response = await fetch("/auth-v2/change-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                identifier: currentUserIdentifier,
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(
                typeof data.detail === "string"
                    ? data.detail
                    : "Password change failed.",
                "error"
            );
            return;
        }

        document.getElementById("currentPassword").value = "";
        document.getElementById("newPassword").value = "";

        showMessage("Password changed successfully.", "success");

    } catch (error) {
        showMessage("Authentication service is unavailable.", "error");
    }
}

function logoutUser() {

    localStorage.removeItem("investedge_identifier");
    localStorage.removeItem("investedge_token");

    sessionStorage.removeItem("investedge_identifier");
    sessionStorage.removeItem("investedge_token");

    currentUserIdentifier = "";

    showLogin();

    showMessage("You have been logged out.", "success");
}
function handleSearch(event) {

    if (event.key !== "Enter") {
        return;
    }

    const symbol = event.target.value.trim();

    if (!symbol) {
        return;
    }

    window.location.href =
        "/research-ui?symbol=" + encodeURIComponent(symbol);
}

function openFeature(name) {

    if (name === "Stocks") {
        const symbol = prompt("Enter stock symbol:", "RELIANCE");

        if (symbol) {
            window.location.href =
                "/research-ui?symbol=" + encodeURIComponent(symbol);
        }

        return;
    }

    alert(name + " workspace is being connected to the MarketPilot engine.");
}

</script>

</body>
</html>
"""






