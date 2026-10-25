$ErrorActionPreference = "Stop"
$root = Get-Location
$main = Join-Path $root "mobile_app\lib\main.dart"

Write-Host "`nInvestEdge quote-safety installer" -ForegroundColor Green
if (!(Test-Path $main)) {
  Write-Host "ERROR: Open PowerShell in your InvestEdge_Combined_Workspace folder first." -ForegroundColor Red
  Write-Host "Expected file: mobile_app\lib\main.dart"
  Read-Host "Press Enter to exit"
  exit 1
}

$src = Get-Content -LiteralPath $main -Raw
foreach ($marker in @("class Stock {", "class MarketEngine {", "class LiveBackend {", "void applyLiveTick(Map<String, dynamic> data)")) {
  if (!$src.Contains($marker)) {
    Write-Host "ERROR: This main.dart is different from the version this patch expects." -ForegroundColor Red
    Write-Host "No changes made."
    Read-Host "Press Enter to exit"
    exit 1
  }
}

$backupDir = Join-Path $root "_investedge_backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$backup = Join-Path $backupDir ("main.dart." + (Get-Date -Format "yyyyMMdd_HHmmss") + ".bak")
Copy-Item -LiteralPath $main -Destination $backup

try {
  # Replace Stock and Holding definitions, and remove the random SignalEngine.
  $stockPattern = '(?s)class Stock\s*\{.*?\nclass Holding\s*\{.*?\n\}'
  $stockReplacement = @'
class Stock {
  final String symbol;
  String name;
  double price;
  double change;
  double rsi;
  double technical;
  double fundamental;
  double momentum;
  double risk;
  double confidence;
  Signal signal;
  DateTime updated;
  bool hasVerifiedQuote;
  String quoteSource;

  Stock({
    required this.symbol,
    required this.name,
    this.price = 0,
    this.change = 0,
    this.rsi = 0,
    this.technical = 0,
    this.fundamental = 0,
    this.momentum = 0,
    this.risk = 0,
    this.signal = Signal.hold,
    this.confidence = 0,
    DateTime? updated,
    this.hasVerifiedQuote = false,
    this.quoteSource = '',
  }) : updated = updated ?? DateTime.fromMillisecondsSinceEpoch(0);
}

class Holding {
  final String symbol;
  double qty;
  double avgPrice;
  Holding(this.symbol, this.qty, this.avgPrice);
}
'@
  $src2 = [regex]::Replace($src, $stockPattern, $stockReplacement, 1)
  if ($src2 -eq $src) { throw "Could not safely locate Stock/Holding definitions." }
  $src = $src2

  # Replace MarketEngine up to LiveBackend with non-simulating implementation.
  $enginePattern = '(?s)class MarketEngine\s*\{.*?\nclass LiveBackend\s*\{'
  $engineReplacement = @'
class MarketEngine {
  final Map<String, Stock> stocks = {};
  final Map<String, String> catalog = {};
  final StreamController<String> _ticks = StreamController.broadcast();
  bool isLive = false;

  Stream<String> get ticks => _ticks.stream;
  bool get hasBackendState => isLive;

  MarketEngine() {
    for (final symbol in universe) {
      stocks[symbol] = Stock(
        symbol: symbol,
        name: names[symbol] ?? '$symbol (NSE)',
      );
    }
  }

  // No simulated price generation.
  void start() {}

  void stopSimulator({bool live = false}) {
    isLive = live;
  }

  void applyLiveTick(Map<String, dynamic> data) {
    if ((data['source'] ?? '').toString().toLowerCase() != 'upstox') return;

    final symbol = (data['symbol'] ?? '').toString().trim().toUpperCase();
    if (symbol.isEmpty) return;

    double? number(dynamic value) {
      if (value is num) {
        final n = value.toDouble();
        return n.isFinite ? n : null;
      }
      final n = double.tryParse('$value');
      return n != null && n.isFinite ? n : null;
    }

    final price = number(data['price']);
    if (price == null || price <= 0) return;

    final s = stocks.putIfAbsent(
      symbol,
      () => Stock(
        symbol: symbol,
        name: catalog[symbol] ?? names[symbol] ?? '$symbol (NSE)',
      ),
    );

    s.price = price;
    s.hasVerifiedQuote = true;
    s.quoteSource = 'upstox';

    final change = number(data['change_percent']) ?? number(data['change']);
    if (change != null) s.change = change;

    final rsi = number(data['rsi']);
    final technical = number(data['technical']);
    final fundamental = number(data['fundamental']);
    final momentum = number(data['momentum']);
    final risk = number(data['risk']);
    final confidence = number(data['confidence']);

    if (rsi != null && rsi >= 0 && rsi <= 100) s.rsi = rsi;
    if (technical != null && technical >= 0 && technical <= 100) s.technical = technical;
    if (fundamental != null && fundamental >= 0 && fundamental <= 100) s.fundamental = fundamental;
    if (momentum != null && momentum >= 0 && momentum <= 100) s.momentum = momentum;
    if (risk != null && risk >= 0 && risk <= 100) s.risk = risk;
    if (confidence != null && confidence >= 0 && confidence <= 100) s.confidence = confidence;

    final signal = (data['signal'] ?? '').toString().toUpperCase();
    if (signal == 'BUY') {
      s.signal = Signal.buy;
    } else if (signal == 'SELL') {
      s.signal = Signal.sell;
    } else if (signal == 'HOLD') {
      s.signal = Signal.hold;
    }

    final updated = number(data['updated']);
    s.updated = updated == null
        ? DateTime.now()
        : DateTime.fromMillisecondsSinceEpoch(updated.toInt());

    isLive = true;
    if (!_ticks.isClosed) _ticks.add(symbol);
  }

  void applyCatalog(List<dynamic> rows) {
    for (final raw in rows) {
      if (raw is! Map) continue;
      final symbol = (raw['symbol'] ?? '').toString().toUpperCase();
      if (symbol.isEmpty) continue;
      final name = (raw['name'] ?? symbol).toString();
      catalog[symbol] = name;
      stocks.putIfAbsent(
        symbol,
        () => Stock(symbol: symbol, name: name),
      ).name = name;
    }
  }

  Stock ensure(String raw) {
    final symbol = raw.trim().toUpperCase().replaceAll(' ', '');
    if (symbol.isEmpty) throw Exception('Enter an NSE symbol.');
    return stocks.putIfAbsent(
      symbol,
      () => Stock(
        symbol: symbol,
        name: catalog[symbol] ?? names[symbol] ?? '$symbol (NSE)',
      ),
    );
  }

  void dispose() {
    _ticks.close();
  }
}

class LiveBackend {
'@
  $src2 = [regex]::Replace($src, $enginePattern, $engineReplacement, 1)
  if ($src2 -eq $src) { throw "Could not safely locate MarketEngine/LiveBackend boundary." }
  $src = $src2

  # Keep dashboard updates on received ticks, but do not treat a status-only message as proof of a live quote.
  $src = $src.Replace("setState(() => market.isLive = source == 'upstox');", "setState(() => market.isLive = false;)")
  # Only allow quote-backed tick handler to set live status.
  $src = $src.Replace("market.applyLiveTick(data);`r`n      if ((data['source'] ?? '').toString().toLowerCase() == 'upstox') {`r`n        market.isLive = true;`r`n      }", "market.applyLiveTick(data);")
  $src = $src.Replace("market.applyLiveTick(data);`n      if ((data['source'] ?? '').toString().toLowerCase() == 'upstox') {`n        market.isLive = true;`n      }", "market.applyLiveTick(data);")

  # Avoid labeling index cards as live merely because the websocket is connected.
  $src = $src.Replace("backendOnline`r`n              ? 'Connected • index feed'`r`n              : subtitle", "'Index feed not connected'")
  $src = $src.Replace("backendOnline ? 'LIVE' : '—'", "'—'")
  $src = $src.Replace("backendOnline`n              ? 'Connected • index feed'`n              : subtitle", "'Index feed not connected'")

  # UI list rows: display waiting status for symbols without verified quotes.
  $src = $src.Replace("'₹${s.price.toStringAsFixed(2)}'", "s.hasVerifiedQuote ? '₹${s.price.toStringAsFixed(2)}' : 'Waiting for tick'")
  $src = $src.Replace("'${s.change >= 0 ? '+' : ''}${s.change.toStringAsFixed(2)}%'", "s.hasVerifiedQuote ? '${s.change >= 0 ? '+' : ''}${s.change.toStringAsFixed(2)}%' : '—'")

  # Do not allow adding a holding at an invented/default price.
  $src = $src.Replace("onPressed: () => addHolding(s),", "onPressed: s.hasVerifiedQuote ? () => addHolding(s) : null,")
  $src = $src.Replace("final qty = TextEditingController(text: '1');`r`n    final avg = TextEditingController(text: s.price.toStringAsFixed(2));", "if (!s.hasVerifiedQuote) {`r`n      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Waiting for a verified Upstox quote.')));`r`n      return;`r`n    }`r`n    final qty = TextEditingController(text: '1');`r`n    final avg = TextEditingController(text: s.price.toStringAsFixed(2));")
  $src = $src.Replace("final qty = TextEditingController(text: '1');`n    final avg = TextEditingController(text: s.price.toStringAsFixed(2));", "if (!s.hasVerifiedQuote) {`n      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Waiting for a verified Upstox quote.')));`n      return;`n    }`n    final qty = TextEditingController(text: '1');`n    final avg = TextEditingController(text: s.price.toStringAsFixed(2));")

  Set-Content -LiteralPath $main -Value $src -Encoding UTF8

  # Verify source markers and run Flutter analysis if available.
  $check = Get-Content -LiteralPath $main -Raw
  if (!$check.Contains("bool hasVerifiedQuote;") -or !$check.Contains("source != 'upstox'")) {
    throw "Post-edit validation failed."
  }

  $flutter = Get-Command flutter -ErrorAction SilentlyContinue
  if ($flutter) {
    Push-Location (Join-Path $root "mobile_app")
    try { flutter analyze } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw "flutter analyze failed." }
  } else {
    Write-Host "Flutter command not found in PATH; source validation passed, but analyzer was not run." -ForegroundColor Yellow
  }

  Write-Host "`nPatch applied. Backup: $backup" -ForegroundColor Green
  Write-Host "Please check the app before making further changes."
} catch {
  Copy-Item -LiteralPath $backup -Destination $main -Force
  Write-Host "`nPatch failed and original main.dart was restored." -ForegroundColor Red
  Write-Host $_.Exception.Message -ForegroundColor Red
}
Read-Host "Press Enter to close"
