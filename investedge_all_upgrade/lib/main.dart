
import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String investEdgeBackendWsUrl = String.fromEnvironment('INVESTEDGE_BACKEND_URL', defaultValue: 'ws://127.0.0.1:8000/ws/market');

void main() => runApp(const InvestEdgeApp());

class InvestEdgeApp extends StatelessWidget {
  const InvestEdgeApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'InvestEdge',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF5F7F6),
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF183B35)),
        fontFamily: 'Arial',
      ),
      home: const InvestEdgeShell(),
    );
  }
}

enum Signal { buy, hold, sell }

class Stock {
  final String symbol;
  String name;
  double price, change, rsi, technical, fundamental, momentum, risk, confidence;
  Signal signal;
  DateTime updated;

  Stock({
    required this.symbol, required this.name, required this.price,
    this.change = 0, this.rsi = 50, this.technical = 50,
    this.fundamental = 60, this.momentum = 50, this.risk = 50,
    this.signal = Signal.hold, this.confidence = 50, DateTime? updated,
  }) : updated = updated ?? DateTime.now();
}

class Holding {
  final String symbol;
  double qty, avgPrice;
  Holding(this.symbol, this.qty, this.avgPrice);
}

class SignalEngine {
  static void update(Stock s, Random r) {
    s.change = (s.change * .85) + (r.nextDouble() - .54) * .9;
    s.price = max(.5, s.price * (1 + s.change / 10000));
    s.rsi = (s.rsi + (r.nextDouble() - .5) * 5).clamp(8, 92);
    s.momentum = (50 + s.change * 8 + (r.nextDouble() - .5) * 15).clamp(0, 100);
    s.technical = (50 + (50 - s.rsi) * .35 + s.momentum * .35).clamp(0, 100);
    s.fundamental = (45 + r.nextDouble() * 45).clamp(0, 100);
    s.risk = (55 - s.change.abs() * 5 + r.nextDouble() * 20).clamp(5, 95);
    final score = s.technical * .35 + s.fundamental * .30 + s.momentum * .20 + s.risk * .15;
    s.signal = score >= 68 ? Signal.buy : score <= 43 ? Signal.sell : Signal.hold;
    s.confidence = (50 + (score - 50).abs() * 1.25).clamp(50, 95);
    s.updated = DateTime.now();
  }
}

const List<String> universe = <String>[
    'RELIANCE',
    'TCS',
    'HDFCBANK',
    'ICICIBANK',
    'INFY',
    'ITC',
    'SBIN',
    'BHARTIARTL',
    'KOTAKBANK',
    'AXISBANK',
    'LT',
    'HINDUNILVR',
    'BAJFINANCE',
    'MARUTI',
    'SUNPHARMA',
    'M&M',
    'HCLTECH',
    'WIPRO',
    'ULTRACEMCO',
    'TITAN',
    'ASIANPAINT',
    'NESTLEIND',
    'TATAMOTORS',
    'TATASTEEL',
    'NTPC',
    'POWERGRID',
    'ONGC',
    'COALINDIA',
    'ADANIENT',
    'ADANIPORTS',
    'ADANIPOWER',
    'JSWSTEEL',
    'JINDALSTEL',
    'GRASIM',
    'EICHERMOT',
    'HEROMOTOCO',
    'BAJAJ-AUTO',
    'TVSMOTOR',
    'APOLLOHOSP',
    'CIPLA',
    'DRREDDY',
    'DIVISLAB',
    'SBILIFE',
    'HDFCLIFE',
    'ICICIPRULI',
    'LTIM',
    'TECHM',
    'INDUSINDBK',
    'BANKBARODA',
    'PNB',
    'CANBK',
    'IDFCFIRSTB',
    'FEDERALBNK',
    'RECLTD',
    'PFC',
    'IRFC',
    'BEL',
    'HAL',
    'BHEL',
    'IOC',
    'BPCL',
    'HPCL',
    'GAIL',
    'TATAPOWER',
    'NHPC',
    'SJVN',
    'VEDL',
    'HINDALCO',
    'JSWENERGY',
    'TRENT',
    'DMART',
    'ZOMATO',
    'NYKAA',
    'DELHIVERY',
    'PAYTM',
    'PERSISTENT',
    'COFORGE',
    'MPHASIS',
    'LTTS',
    'DIXON',
    'KPIT',
    'CYIENT',
    'SUPREMEIND',
    'ASTRAL',
    'POLYCAB',
    'KEI',
    'HAVELLS',
    'VOLTAS',
    'CROMPTON',
    'DABUR',
    'GODREJCP',
    'MARICO',
    'COLPAL',
    'BRITANNIA',
    'PIDILITIND',
    'BERGEPAINT',
    'GODREJPROP',
    'DLF',
    'OBEROIRLTY',
    'PRESTIGE',
    'PHOENIXLTD',
    'LODHA',
    'SHREECEM',
    'AMBUJACEM',
    'ACC',
    'DALBHARAT',
    'RAMCOCEM',
    'JKLAKSHMI',
    'INDHOTEL',
    'EIH',
    'IRCTC',
    'CONCOR',
    'RVNL',
    'RITES',
    'MOTHERSON',
    'BOSCHLTD',
    'ASHOKLEY',
    'ESCORTS',
    'EXIDEIND',
    'SIEMENS',
    'ABB',
    'INDIGO',
    'MAXHEALTH',
    'FORTIS',
    'LAURUSLABS',
    'AUROPHARMA',
    'ALKEM',
    'LUPIN',
    'BIOCON',
    'GLENMARK',
    'TORNTPHARM',
    'ZYDUSLIFE',
    'IPCA',
    'NATCOPHARM',
    'AJANTAPHARM',
    'ICICIGI',
    'GICRE',
    'CHOLAFIN',
    'MUTHOOTFIN',
    'MANAPPURAM',
    'SHRIRAMFIN',
    'LICHSGFIN',
    'POLICYBZR',
    'ANGELONE',
    'MCX',
    'BSE',
    'CDSL',
    'IEX',
    'CAMS',
    'KFINTECH',
    'RBLBANK',
    'BANDHANBNK',
    'IDBI',
    'INDIANB',
    'UCOBANK',
    'UNIONBANK',
    'MAHABANK',
    'IOB',
    'SAIL',
    'NMDC',
    'NATIONALUM',
    'HINDZINC',
    'JSL',
    'MGL',
    'IGL',
    'PETRONET',
    'APLAPOLLO',
    'INOXWIND',
    'SUZLON',
    'ZEEL',
    'PVRINOX',
    'SUNTV',
    'ABFRL',
    'BATAINDIA',
    'PAGEIND',
    'KALYANKJIL',
    'INDIAMART',
    'NAUKRI',
    'INFOEDGE',
    'EASEMYTRIP',
    'NBCC',
    'NLCINDIA',
    'HUDCO',
    'IREDA',
    'KPIGREEN',
    'YESBANK',
    'JUBLFOOD',
    'SRF',
    'DEEPAKNTR',
    'ATUL',
    'AARTIIND',
    'PIIND',
    'COROMANDEL',
    'UPL',
    'FINEORG',
    'VINATIORGA',
    'ALKYLAMINE',
    'DEEPAKFERT',
    'GNFC',
    'CHAMBLFERT',
    'CANFINHOME',
    'LICI'
];

const Map<String, String> names = <String, String>{
    'RELIANCE': 'Reliance Industries',
    'TCS': 'Tata Consultancy Services',
    'HDFCBANK': 'HDFC Bank',
    'ICICIBANK': 'ICICI Bank',
    'INFY': 'Infosys',
    'ITC': 'ITC',
    'SBIN': 'State Bank of India',
    'BHARTIARTL': 'Bharti Airtel',
    'KOTAKBANK': 'Kotak Mahindra Bank',
    'AXISBANK': 'Axis Bank',
    'LT': 'Larsen & Toubro',
    'HINDUNILVR': 'Hindustan Unilever',
    'BAJFINANCE': 'Bajaj Finance',
    'MARUTI': 'Maruti Suzuki India',
    'SUNPHARMA': 'Sun Pharmaceutical Industries',
    'M&M': 'Mahindra & Mahindra',
    'HCLTECH': 'HCL Technologies',
    'WIPRO': 'Wipro',
    'TITAN': 'Titan Company',
    'TATAMOTORS': 'Tata Motors',
    'TATASTEEL': 'Tata Steel',
    'NTPC': 'NTPC',
    'POWERGRID': 'Power Grid Corporation',
    'ONGC': 'Oil & Natural Gas Corporation',
    'COALINDIA': 'Coal India',
    'ADANIENT': 'Adani Enterprises',
    'ADANIPORTS': 'Adani Ports',
    'JSWSTEEL': 'JSW Steel',
    'ZOMATO': 'Eternal (Zomato)',
    'PAYTM': 'One97 Communications',
    'DMART': 'Avenue Supermarts',
    'TRENT': 'Trent',
    'IRCTC': 'Indian Railway Catering & Tourism Corporation',
    'HAL': 'Hindustan Aeronautics',
    'BEL': 'Bharat Electronics',
    'LICI': 'Life Insurance Corporation of India',
    'YESBANK': 'Yes Bank',
    'BSE': 'BSE Ltd',
    'CDSL': 'Central Depository Services',
    'MCX': 'Multi Commodity Exchange',
    'NAUKRI': 'Info Edge',
    'INDIGO': 'InterGlobe Aviation',
    'DLF': 'DLF'
};

class MarketEngine {
  final Random random = Random();
  final Map<String, Stock> stocks = {};
  final Map<String, String> catalog = {};
  final StreamController<String> _ticks = StreamController.broadcast();
  Timer? _timer;
  bool isLive = false;
  bool get hasBackendState => isLive;

  Stream<String> get ticks => _ticks.stream;

  MarketEngine() {
    for (final symbol in universe) {
      final s = Stock(
        symbol: symbol,
        name: catalog[symbol] ?? names[symbol] ?? '$symbol (NSE)',
        price: 40 + random.nextInt(16000).toDouble(),
        change: (random.nextDouble() - .5) * 2,
        rsi: 30 + random.nextDouble() * 40,
      );
      SignalEngine.update(s, random);
      stocks[symbol] = s;
    }
    stocks['RELIANCE']?.price = 1178;
    stocks['TCS']?.price = 2076;
    stocks['HDFCBANK']?.price = 692.25;
    stocks['ICICIBANK']?.price = 1349;
  }

  void start() {
    _timer ??= Timer.periodic(const Duration(milliseconds: 1200), (_) {
      final keys = stocks.keys.toList();
      for (int i = 0; i < min(35, keys.length); i++) {
        final key = keys[random.nextInt(keys.length)];
        final stock = stocks[key];
        if (stock != null) SignalEngine.update(stock, random);
        _ticks.add(key);
      }
    });
  }

  void stopSimulator({bool live = false}) {
    _timer?.cancel();
    _timer = null;
    isLive = live;
  }

  void applyLiveTick(Map<String, dynamic> data) {
    final symbol = (data['symbol'] ?? '').toString().toUpperCase();
    if (symbol.isEmpty) return;
    final s = stocks.putIfAbsent(symbol, () => Stock(symbol: symbol, name: catalog[symbol] ?? names[symbol] ?? '$symbol (NSE)', price: 100));
    s.price = (data['price'] as num?)?.toDouble() ?? s.price;
    s.change = (data['change'] as num?)?.toDouble() ?? s.change;
    s.rsi = (data['rsi'] as num?)?.toDouble() ?? s.rsi;
    s.technical = (data['technical'] as num?)?.toDouble() ?? s.technical;
    s.fundamental = (data['fundamental'] as num?)?.toDouble() ?? s.fundamental;
    s.momentum = (data['momentum'] as num?)?.toDouble() ?? s.momentum;
    s.risk = (data['risk'] as num?)?.toDouble() ?? s.risk;
    s.confidence = (data['confidence'] as num?)?.toDouble() ?? s.confidence;
    final signal = (data['signal'] ?? 'HOLD').toString().toUpperCase();
    s.signal = signal == 'BUY' ? Signal.buy : signal == 'SELL' ? Signal.sell : Signal.hold;
    final updated = int.tryParse('${data['updated'] ?? ''}');
    if (updated != null) s.updated = DateTime.fromMillisecondsSinceEpoch(updated);
  }

  void applyCatalog(List<dynamic> rows) {
    for (final raw in rows) {
      if (raw is! Map) continue;
      final symbol = (raw['symbol'] ?? '').toString().toUpperCase();
      if (symbol.isEmpty) continue;
      final name = (raw['name'] ?? symbol).toString();
      catalog[symbol] = name;
      final existing = stocks[symbol];
      if (existing != null) existing.name = name;
    }
  }

  void dispose() {
    _timer?.cancel();
    _ticks.close();
  }

  Stock ensure(String raw) {
    final symbol = raw.trim().toUpperCase().replaceAll(' ', '');
    if (symbol.isEmpty) throw Exception('Enter an NSE symbol.');
    return stocks.putIfAbsent(symbol, () {
      final s = Stock(
        symbol: symbol,
        name: catalog[symbol] ?? names[symbol] ?? '$symbol (NSE)',
        price: 100 + random.nextInt(4000).toDouble(),
        rsi: 45 + random.nextDouble() * 10,
      );
      SignalEngine.update(s, random);
      return s;
    });
  }
}

class LiveBackend {
  LiveBackend({this.url = investEdgeBackendWsUrl});
  final String url;
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool connected = false;

  Future<void> connect({required void Function(Map<String, dynamic>) onMessage, required void Function(bool) onConnection}) async {
    try {
      final channel = WebSocketChannel.connect(Uri.parse(url));
      _channel = channel;
      await channel.ready;
      connected = true;
      onConnection(true);
      _subscription = channel.stream.listen((event) {
        try {
          final data = jsonDecode(event.toString());
          if (data is Map<String, dynamic>) onMessage(data);
        } catch (_) {}
      }, onDone: () { connected = false; onConnection(false); }, onError: (_) { connected = false; onConnection(false); });
    } catch (_) {
      connected = false;
      onConnection(false);
    }
  }

  void subscribe(List<String> symbols) {
    if (!connected) return;
    _channel?.sink.add(jsonEncode({'action':'subscribe','symbols':symbols}));
  }

  Future<void> dispose() async {
    await _subscription?.cancel();
    await _channel?.sink.close();
  }
}

class InvestEdgeShell extends StatefulWidget {
  const InvestEdgeShell({super.key});
  @override
  State<InvestEdgeShell> createState() => _InvestEdgeShellState();
}

class _InvestEdgeShellState extends State<InvestEdgeShell> {
  final MarketEngine market = MarketEngine();
  final LiveBackend backend = LiveBackend();
  final List<String> watchlist = [
    'RELIANCE','TCS','HDFCBANK','ICICIBANK','INFY','ITC','AXISBANK','SBIN'
  ];
  final Map<String, Holding> portfolio = {};
  int tab = 0;
  String? selected;
  bool locked = false;
  bool backendOnline = false;
  final TextEditingController _researchController = TextEditingController();

  @override
  void dispose() {
    _researchController.dispose();
    backend.dispose();
    market.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    market.start();
    market.ticks.listen((_) { if (mounted) setState(() {}); });
    _loadLocalState();
    backend.connect(
      onConnection: (online) {
        if (!mounted) return;
        setState(() { backendOnline = online; });
        if (online) {
          market.stopSimulator(live: false);
          backend.subscribe(watchlist);
        }
      },
      onMessage: (data) {
        if (!mounted) return;
        if (data['type'] == 'status') {
          final source = (data['source'] ?? '').toString();
          setState(() { market.isLive = source == 'upstox'; });
        } else if (data['type'] == 'catalog') {
          market.applyCatalog((data['stocks'] as List?) ?? const []);
          setState(() {});
        } else if (data['type'] == 'tick') {
          market.applyLiveTick(data);
          if ((data['source'] ?? '').toString() == 'upstox') market.isLive = true;
          setState(() {});
        }
      },
    );
  }

  Future<void> _loadLocalState() async {
    final prefs = await SharedPreferences.getInstance();
    final savedWatch = prefs.getStringList('watchlist');
    if (savedWatch != null && savedWatch.isNotEmpty) {
      watchlist..clear()..addAll(savedWatch);
    }
    final raw = prefs.getString('portfolio');
    if (raw != null) {
      try {
        final list = jsonDecode(raw) as List;
        for (final item in list) {
          final m = Map<String, dynamic>.from(item);
          portfolio[m['symbol'].toString()] = Holding(m['symbol'].toString(), (m['qty'] as num).toDouble(), (m['avgPrice'] as num).toDouble());
        }
      } catch (_) {}
    }
    if (mounted) setState(() {});
  }

  Future<void> _saveWatchlist() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('watchlist', watchlist);
  }

  Future<void> _savePortfolio() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('portfolio', jsonEncode(portfolio.values.map((h) => {'symbol':h.symbol,'qty':h.qty,'avgPrice':h.avgPrice}).toList()));
  }

  @override
  void dispose() {
    market.dispose();
    backend.dispose();
    super.dispose();
  }

  Stock get(String symbol) {
    final clean = symbol.trim().toUpperCase().replaceAll(' ', '');
    return market.ensure(clean);
  }

  void openStock(String symbol) {
    final sym = symbol.trim().toUpperCase().replaceAll(' ', '');
    if (sym.isEmpty) return;
    final existsInCatalog = market.catalog.isEmpty || market.catalog.containsKey(sym);
    if (!existsInCatalog && !market.stocks.containsKey(sym)) {
      return;
    }
    get(sym);
    setState(() { selected = sym; tab = 1; });
    backend.subscribe({...watchlist, sym}.toList());
  }

  void toggleWatch(String symbol) {
    setState(() {
      watchlist.contains(symbol) ? watchlist.remove(symbol) : watchlist.add(symbol);
    });
    _saveWatchlist();
    backend.subscribe(watchlist);
  }

  @override
  Widget build(BuildContext context) {
    if (locked) return lockScreen();
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: Row(children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: const Color(0xFF183B35), borderRadius: BorderRadius.circular(10)),
            child: const Text('IE', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900)),
          ),
          const SizedBox(width: 10),
          const Text('InvestEdge', style: TextStyle(fontWeight: FontWeight.w800)),
          const Spacer(),
          liveBadge(),
          IconButton(onPressed: () => setState(() => locked = true), icon: const Icon(Icons.lock_outline)),
        ]),
      ),
      body: SafeArea(child: body()),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() { tab = i; selected = null; }),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Research'),
          NavigationDestination(icon: Icon(Icons.star_border), selectedIcon: Icon(Icons.star), label: 'Watchlist'),
          NavigationDestination(icon: Icon(Icons.account_balance_wallet_outlined), label: 'Portfolio'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Account'),
        ],
      ),
    );
  }

  Widget liveBadge() => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
    decoration: BoxDecoration(color: const Color(0xFFE7F6EE), borderRadius: BorderRadius.circular(20)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(Icons.circle, size: 8, color: market.hasBackendState ? Colors.green : Colors.orange), const SizedBox(width: 6),
      Text(market.hasBackendState ? 'LIVE' : 'DEMO', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
    ]),
  );

  Widget body() {
    if (tab == 0) return home();
    if (tab == 1) {
      final symbol = selected;
      return symbol == null ? research() : detail(get(symbol));
    }
    if (tab == 2) return watch();
    if (tab == 3) return portfolioPage();
    return account();
  }

  Widget home() => ListView(
    padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
    children: [
      const Text('Hi Kshitij! 👋', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900)),
      const SizedBox(height: 5),
      const Text('Track. Analyse. Invest Smarter.', style: TextStyle(fontSize: 16, color: Colors.black54)),
      const SizedBox(height: 18),
      sectionTitle('Live Market', 'Live state updates'),
      const SizedBox(height: 10),
      ...['RELIANCE','TCS','HDFCBANK','ICICIBANK'].map((s) => stockCard(get(s), compact: true)),
      actionCard(Icons.auto_awesome, 'AI Market Research',
        'Search any NSE symbol, analyse it, and add it to your watchlist.',
        () => setState(() => tab = 1)),
      actionCard(Icons.security, 'Security',
        'The Flutter client must never contain Upstox or AI secret keys. Production credentials belong on a secure backend.',
        () => setState(() => tab = 4)),
    ],
  );

  Widget research() {
    final q = _researchController.text.trim().toUpperCase();
    final symbols = market.catalog.keys.toList()..sort();
    final sourceSymbols = symbols.isNotEmpty ? symbols : (market.stocks.keys.toList()..sort());
    final results = q.isEmpty
        ? sourceSymbols.take(100).toList()
        : sourceSymbols.where((symbol) {
            final name = market.catalog[symbol] ?? market.stocks[symbol]?.name ?? symbol;
            final upperName = name.toUpperCase();
            return symbol.contains(q) || upperName.contains(q);
          }).take(100).toList();

    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
      children: [
        const Text('Research', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
        const SizedBox(height: 6),
        const Text('Search the complete available NSE equity universe. Live prices stream when subscribed.', style: TextStyle(color: Colors.black54)),
        const SizedBox(height: 16),
        TextField(
          controller: _researchController,
          textCapitalization: TextCapitalization.characters,
          onChanged: (_) { if (mounted) setState(() {}); },
          onSubmitted: (v) { if (v.trim().isNotEmpty) openStock(v); },
          decoration: InputDecoration(
            hintText: 'Search stock symbol or company name',
            prefixIcon: const Icon(Icons.search),
            suffixIcon: IconButton(
              icon: const Icon(Icons.arrow_forward),
              onPressed: () { final v = _researchController.text.trim(); if (v.isNotEmpty) openStock(v); },
            ),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 14),
        Row(children: [
          stat('NSE Equity', '${market.catalog.isNotEmpty ? market.catalog.length : market.stocks.length}+'),
          stat('Watchlist', '${watchlist.length}'),
          stat('Data', market.isLive ? 'UPSTOX' : 'DEMO'),
        ]),
        const SizedBox(height: 12),
        if (results.isEmpty && q.isNotEmpty)
          empty('No NSE match found', 'Try a symbol such as INFY, SBIN, RELIANCE or search by company name.')
        else
          ...results.map((symbol) => stockCard(get(symbol), showStar: true)),
      ],
    );
  }

  Widget watch() => ListView(
    padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
    children: [
      const Text('Watchlist', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
      const SizedBox(height: 5),
      Text('${watchlist.length} symbols • live state updates', style: const TextStyle(color: Colors.black54)),
      const SizedBox(height: 14),
      if (watchlist.isEmpty) empty('No stocks yet', 'Search any NSE symbol and tap the star to add it.')
      else ...watchlist.map((s) => stockCard(get(s), showStar: true)),
    ],
  );

  Widget portfolioPage() {
    double total = 0;
    for (final h in portfolio.values) total += h.qty * get(h.symbol).price;
    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
      children: [
        const Text('Portfolio', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
        const SizedBox(height: 5),
        const Text('Client portfolio state • ready for secure broker sync', style: TextStyle(color: Colors.black54)),
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(color: const Color(0xFF183B35), borderRadius: BorderRadius.circular(20)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Portfolio Value', style: TextStyle(color: Colors.white70)),
            const SizedBox(height: 6),
            Text('₹${total.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white, fontSize: 30, fontWeight: FontWeight.w900)),
            const SizedBox(height: 8),
            Text('${portfolio.length} holdings', style: const TextStyle(color: Colors.white70)),
          ]),
        ),
        const SizedBox(height: 14),
        ...portfolio.values.map(holdingCard),
        if (portfolio.isEmpty) empty('Portfolio is empty', 'Open a stock and use Add Holding to create a position.'),
      ],
    );
  }

  Widget account() => ListView(
    padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
    children: [
      const Text('Account & Security', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
      const SizedBox(height: 14),
      actionCard(Icons.lock, 'Lock app', 'Instantly lock the current session.', () => setState(() => locked = true)),
      actionCard(Icons.cloud_done, 'Production architecture',
        backendOnline ? 'Connected: Flutter → secure backend → live market state.' : 'Backend is optional locally; the app safely falls back to DEMO data until the backend is running.', () {}),
      actionCard(Icons.android, 'Android ready',
        'The client uses Flutter widgets and is structured for the same UI on Android.', () {}),
      actionCard(Icons.info_outline, 'About InvestEdge',
        'Track. Analyse. Invest Smarter. AI market research, risk intelligence, watchlist and portfolio.', () {}),
    ],
  );

  Widget lockScreen() => Scaffold(
    backgroundColor: const Color(0xFF183B35),
    body: Center(
      child: Card(
        margin: const EdgeInsets.all(28),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.lock, size: 52, color: Color(0xFF183B35)),
            const SizedBox(height: 14),
            const Text('InvestEdge Locked', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
            const SizedBox(height: 8),
            const Text('Unlock this session to continue.'),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: () => setState(() => locked = false),
              icon: const Icon(Icons.lock_open),
              label: const Text('Unlock Session'),
            ),
          ]),
        ),
      ),
    ),
  );

  Widget detail(Stock s) {
    final fav = watchlist.contains(s.symbol);
    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 12, 18, 30),
      children: [
        Row(children: [
          IconButton(onPressed: () => setState(() => selected = null), icon: const Icon(Icons.arrow_back)),
          Expanded(child: Text(s.symbol, style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w900))),
          IconButton(onPressed: () => toggleWatch(s.symbol), icon: Icon(fav ? Icons.star : Icons.star_border)),
        ]),
        Text(s.name, style: const TextStyle(color: Colors.black54)),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFFFFFFFF), Color(0xFFEAF3F0)]), borderRadius: BorderRadius.circular(22), border: Border.all(color: Color(0xFFDCE8E4))),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('₹${s.price.toStringAsFixed(2)}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900)),
            const SizedBox(height: 4),
            Text('${s.change >= 0 ? '+' : ''}${s.change.toStringAsFixed(2)}%',
              style: TextStyle(fontWeight: FontWeight.w800, color: s.change >= 0 ? Colors.green : Colors.red)),
            const SizedBox(height: 12),
            signalChip(s.signal, large: true),
            const SizedBox(height: 8),
            Text('Confidence ${s.confidence.toStringAsFixed(1)}%', style: const TextStyle(fontWeight: FontWeight.w700)),
          ]),
        ),
        const SizedBox(height: 12),
        scoreGrid(s),
        const SizedBox(height: 12),
        levels(s),
        const SizedBox(height: 12),
        actionCard(Icons.auto_awesome, 'AI Market Insight', insight(s), () {}),
        const SizedBox(height: 4),
        FilledButton.icon(onPressed: () => addHolding(s), icon: const Icon(Icons.add_chart), label: const Text('Add Holding')),
        const SizedBox(height: 10),
        Text('Updated ${time(s.updated)} • ${market.isLive ? 'UPSTOX LIVE' : 'DEMO ENGINE'}', style: const TextStyle(color: Colors.black45, fontSize: 12)),
      ],
    );
  }

  String insight(Stock s) {
    final bias = s.signal == Signal.buy ? 'bullish' : s.signal == Signal.sell ? 'bearish' : 'mixed';
    final rsiText = s.rsi < 30 ? 'RSI is oversold' : s.rsi > 70 ? 'RSI is overbought' : 'RSI is in a normal zone';
    return 'The current setup is $bias. $rsiText. Technical ${s.technical.toStringAsFixed(0)}/100, '
      'fundamental ${s.fundamental.toStringAsFixed(0)}/100, momentum ${s.momentum.toStringAsFixed(0)}/100 '
      'and risk ${s.risk.toStringAsFixed(0)}/100. This is an analytical signal, not a guaranteed outcome.';
  }

  Widget scoreGrid(Stock s) => GridView.count(
    crossAxisCount: MediaQuery.of(context).size.width > 900 ? 4 : 2,
    shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
    crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: 2.7,
    children: [metric('Technical', s.technical), metric('Fundamental', s.fundamental),
      metric('Momentum', s.momentum), metric('Risk', s.risk)],
  );

  Widget metric(String label, double value) => Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: const Color(0xFFF0F4F2), borderRadius: BorderRadius.circular(15), border: Border.all(color: const Color(0xFFDDE7E3))),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [
      Row(children: [Expanded(child: Text(label, style: const TextStyle(color: Colors.black54, fontSize: 12))),
        Text(value.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18))]),
      const SizedBox(height: 8),
      ClipRRect(borderRadius: BorderRadius.circular(8), child: LinearProgressIndicator(value: value.clamp(0, 100) / 100, minHeight: 7, backgroundColor: const Color(0xFFDDE7E3), valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF2E6F63)))),
    ]),
  );

  Widget levels(Stock s) {
    final buy = s.signal == Signal.buy;
    final sell = s.signal == Signal.sell;
    final entryLow = buy ? s.price * .995 : sell ? s.price * .985 : s.price * .99;
    final entryHigh = buy ? s.price * 1.005 : sell ? s.price * 1.015 : s.price * 1.01;
    final target1 = buy ? s.price * 1.04 : sell ? s.price * .96 : s.price * 1.02;
    final target2 = buy ? s.price * 1.08 : sell ? s.price * .92 : s.price * 1.04;
    final stop = buy ? s.price * .965 : sell ? s.price * 1.035 : s.price * .97;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFFF0F4F2), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDDE7E3))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [const Expanded(child: Text('Trade Levels', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18))), signalChip(s.signal)]),
        const SizedBox(height: 12),
        level('Entry Zone', '₹${entryLow.toStringAsFixed(2)} – ₹${entryHigh.toStringAsFixed(2)}'),
        level('Target 1', '₹${target1.toStringAsFixed(2)}'),
        level('Target 2', '₹${target2.toStringAsFixed(2)}'),
        level('Stop Loss', '₹${stop.toStringAsFixed(2)}'),
      ]),
    );
  }

  Widget level(String a, String b) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Row(children: [Expanded(child: Text(a, style: const TextStyle(color: Colors.black54))),
      Text(b, style: const TextStyle(fontWeight: FontWeight.w800))]),
  );

  Widget stockCard(Stock s, {bool compact = false, bool showStar = false}) => Card(
    elevation: 0,
    margin: const EdgeInsets.only(bottom: 9),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17)),
    child: InkWell(
      borderRadius: BorderRadius.circular(17),
      onTap: () => openStock(s.symbol),
      child: Padding(
        padding: EdgeInsets.all(compact ? 14 : 13),
        child: Row(children: [
          Container(
            width: 44, height: 44, alignment: Alignment.center,
            decoration: BoxDecoration(color: const Color(0xFFE8F0EE), borderRadius: BorderRadius.circular(12)),
            child: Text(s.symbol.substring(0, min(2, s.symbol.length)),
              style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF183B35))),
          ),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(s.symbol, style: const TextStyle(fontWeight: FontWeight.w900)),
            Text(s.name, maxLines: 1, overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 12, color: Colors.black54)),
          ])),
          Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
            Text('₹${s.price.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w800)),
            Text('${s.change >= 0 ? '+' : ''}${s.change.toStringAsFixed(2)}%',
              style: TextStyle(fontSize: 12, color: s.change >= 0 ? Colors.green : Colors.red)),
          ]),
          const SizedBox(width: 9),
          signalChip(s.signal),
          if (showStar) IconButton(onPressed: () => toggleWatch(s.symbol),
            icon: const Icon(Icons.star, color: Color(0xFFFFB300))),
        ]),
      ),
    ),
  );

  Widget signalChip(Signal signal, {bool large = false}) {
    final label = signal == Signal.buy ? 'BUY' : signal == Signal.sell ? 'SELL' : 'HOLD';
    final color = signal == Signal.buy ? Colors.green : signal == Signal.sell ? Colors.red : Colors.orange;
    return Container(
      padding: EdgeInsets.symmetric(horizontal: large ? 14 : 9, vertical: large ? 8 : 5),
      decoration: BoxDecoration(color: color.withOpacity(.11), borderRadius: BorderRadius.circular(20)),
      child: Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w900, fontSize: large ? 15 : 10)),
    );
  }

  Widget holdingCard(Holding h) {
    final s = get(h.symbol), value = h.qty * s.price, pnl = (s.price - h.avgPrice) * h.qty;
    return Card(
      elevation: 0,
      child: ListTile(
        onTap: () => openStock(h.symbol),
        title: Text(h.symbol, style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Text('${h.qty} qty • avg ₹${h.avgPrice.toStringAsFixed(2)}'),
        trailing: Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
          Text('₹${value.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w800)),
          Text('${pnl >= 0 ? '+' : ''}₹${pnl.toStringAsFixed(2)}', style: TextStyle(color: pnl >= 0 ? Colors.green : Colors.red)),
        ]),
      ),
    );
  }

  void addHolding(Stock s) {
    final qty = TextEditingController(text: '1');
    final avg = TextEditingController(text: s.price.toStringAsFixed(2));
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Add ${s.symbol}'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: qty, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Quantity')),
          TextField(controller: avg, keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Average price')),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(onPressed: () {
            final q = double.tryParse(qty.text) ?? 0;
            final p = double.tryParse(avg.text) ?? s.price;
            if (q > 0) { setState(() => portfolio[s.symbol] = Holding(s.symbol, q, p)); _savePortfolio(); }
            Navigator.pop(context);
          }, child: const Text('Save')),
        ],
      ),
    );
  }

  Widget actionCard(IconData icon, String title, String body, VoidCallback onTap) => Card(
    elevation: 0,
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      leading: CircleAvatar(backgroundColor: const Color(0xFFE8F0EE), child: Icon(icon, color: const Color(0xFF183B35))),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
      subtitle: Padding(padding: const EdgeInsets.only(top: 4), child: Text(body)),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    ),
  );

  Widget sectionTitle(String a, String b) => Row(children: [
    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(a, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
      Text(b, style: const TextStyle(color: Colors.black45, fontSize: 12)),
    ])),
  ]);

  Widget stat(String a, String b) => Expanded(
    child: Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(a, style: const TextStyle(fontSize: 11, color: Colors.black54)),
        Text(b, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
      ]),
    ),
  );

  Widget empty(String title, String body) => Container(
    padding: const EdgeInsets.all(24),
    decoration: BoxDecoration(color: const Color(0xFFF0F4F2), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDDE7E3))),
    child: Column(children: [
      const Icon(Icons.inbox_outlined, size: 44, color: Colors.black38),
      const SizedBox(height: 8),
      Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
      const SizedBox(height: 5),
      Text(body, textAlign: TextAlign.center, style: const TextStyle(color: Colors.black54)),
    ]),
  );

  String time(DateTime d) =>
      '${d.hour.toString().padLeft(2,'0')}:${d.minute.toString().padLeft(2,'0')}:${d.second.toString().padLeft(2,'0')}';
}
