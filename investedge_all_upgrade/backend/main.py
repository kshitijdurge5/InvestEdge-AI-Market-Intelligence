import asyncio
import gzip
import hashlib
import hmac
import json
import os
import random
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'development')
JWT_SECRET = os.getenv('JWT_SECRET', 'CHANGE_ME_IN_PRODUCTION')
DATABASE_URL = os.getenv('DATABASE_URL', 'data/investedge.db')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://api.deepseek.com/v1')
AI_MODEL = os.getenv('AI_MODEL', 'deepseek-chat')
UPSTOX_ACCESS_TOKEN = os.getenv('UPSTOX_ACCESS_TOKEN', '')
NSE_INSTRUMENTS_URL = os.getenv('NSE_INSTRUMENTS_URL', 'https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz')
USE_SIMULATOR = os.getenv('USE_SIMULATOR', 'true').lower() == 'true'

os.makedirs(os.path.dirname(DATABASE_URL) or '.', exist_ok=True)

def db():
    con = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

con = db()
con.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS watchlist(user_id INTEGER NOT NULL, symbol TEXT NOT NULL, UNIQUE(user_id, symbol));
CREATE TABLE IF NOT EXISTS holdings(user_id INTEGER NOT NULL, symbol TEXT NOT NULL, qty REAL NOT NULL, avg_price REAL NOT NULL, UNIQUE(user_id, symbol));
''')
con.commit()

DEFAULT_SYMBOLS = ['RELIANCE','TCS','HDFCBANK','ICICIBANK','INFY','ITC','AXISBANK','SBIN']
# Stable NSE equity instrument keys used for the first live subscription set.
INSTRUMENT_KEYS = {
    'RELIANCE': 'NSE_EQ|INE002A01018',
    'TCS': 'NSE_EQ|INE467B01029',
    'HDFCBANK': 'NSE_EQ|INE040A01034',
    'ICICIBANK': 'NSE_EQ|INE090A01021',
    'INFY': 'NSE_EQ|INE009A01021',
    'ITC': 'NSE_EQ|INE154A01025',
    'AXISBANK': 'NSE_EQ|INE238A01034',
    'SBIN': 'NSE_EQ|INE062A01020',
}

state: dict[str, dict[str, Any]] = {}
clients: set[WebSocket] = set()
loop: asyncio.AbstractEventLoop | None = None
upstox_thread: threading.Thread | None = None
upstox_streamer = None
upstox_streamer_lock = threading.Lock()

BASE_PRICES = {'RELIANCE':1177.8,'TCS':2076.2,'HDFCBANK':692.3,'ICICIBANK':1349.0,'INFY':1540.0,'ITC':410.0,'AXISBANK':1240.0,'SBIN':1040.0}

# Full NSE equity catalog. This is refreshed from Upstox's official daily instrument JSON.
# It is a catalog only; live prices are streamed for subscribed symbols.
instrument_catalog: dict[str, dict[str, str]] = {}

def load_nse_catalog():
    global instrument_catalog
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(NSE_INSTRUMENTS_URL)
            response.raise_for_status()
            raw = gzip.decompress(response.content)
        rows = json.loads(raw.decode('utf-8'))
        catalog = {}
        for item in rows:
            if item.get('segment') != 'NSE_EQ':
                continue
            if item.get('instrument_type') not in ('EQ', 'BE'):
                continue
            symbol = str(item.get('trading_symbol') or '').strip().upper()
            if not symbol:
                continue
            catalog[symbol] = {
                'symbol': symbol,
                'name': str(item.get('short_name') or item.get('name') or symbol),
                'instrument_key': str(item.get('instrument_key') or ''),
            }
        if catalog:
            instrument_catalog = catalog
            print(f'Loaded {len(instrument_catalog)} NSE equity instruments.')
    except Exception as exc:
        print(f'NSE catalog refresh failed; using built-in catalog: {exc}')
        instrument_catalog = {s: {'symbol': s, 'name': s, 'instrument_key': INSTRUMENT_KEYS.get(s, '')} for s in DEFAULT_SYMBOLS}


def signal_for(price: float, change: float) -> dict[str, float | str]:
    momentum = max(0.0, min(100.0, 50 + change * 10))
    technical = max(0.0, min(100.0, 58 + change * 12))
    fundamental = 72.0
    risk = max(10.0, min(95.0, 58 - abs(change) * 6))
    score = technical*.35 + fundamental*.30 + momentum*.20 + risk*.15
    signal = 'BUY' if score >= 68 else 'SELL' if score <= 43 else 'HOLD'
    confidence = max(50.0, min(95.0, 50 + abs(score-50)*1.25))
    return {'technical':technical,'fundamental':fundamental,'momentum':momentum,'risk':risk,'score':score,'signal':signal,'confidence':confidence}

def set_tick(symbol: str, price: float, change: float, updated_ms: int | None = None):
    s = signal_for(price, change)
    state[symbol] = {'symbol':symbol,'price':price,'change':change,'rsi':50.0,'technical':s['technical'],'fundamental':s['fundamental'],'momentum':s['momentum'],'risk':s['risk'],'signal':s['signal'],'confidence':s['confidence'],'updated':updated_ms or int(time.time()*1000),'source':'upstox'}

load_nse_catalog()
for sym, px in BASE_PRICES.items():
    set_tick(sym, px, 0.0)

class LoginBody(BaseModel):
    email: str
    password: str

class HoldingBody(BaseModel):
    symbol: str
    qty: float
    avg_price: float

class WatchBody(BaseModel):
    symbol: str


def pw_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 210_000).hex()
    return f'{salt}${digest}'

def pw_ok(password: str, encoded: str) -> bool:
    try:
        salt, digest = encoded.split('$',1)
        check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 210_000).hex()
        return hmac.compare_digest(check, digest)
    except Exception:
        return False

def token_for(user_id: int) -> str:
    return jwt.encode({'sub': str(user_id), 'iat': int(time.time()), 'exp': int(time.time())+86400*7}, JWT_SECRET, algorithm='HS256')

def user_id_from_token(token: str) -> int:
    try:
        return int(jwt.decode(token, JWT_SECRET, algorithms=['HS256'])['sub'])
    except Exception:
        raise HTTPException(401, 'Invalid or expired token')

def normalize_symbol(s: str) -> str:
    return s.strip().upper().replace(' ','')

def broadcast(payload: dict[str, Any]):
    if not loop:
        return
    dead = []
    async def send_all():
        for ws in list(clients):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            clients.discard(ws)
    asyncio.run_coroutine_threadsafe(send_all(), loop)

def upstox_worker():
    global upstox_streamer
    try:
        import upstox_client
        configuration = upstox_client.Configuration()
        configuration.access_token = UPSTOX_ACCESS_TOKEN
        keys = [v['instrument_key'] for v in instrument_catalog.values() if v.get('instrument_key')]
        if not keys:
            keys = list(INSTRUMENT_KEYS.values())
        streamer = upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(configuration), keys, 'ltpc')
        with upstox_streamer_lock:
            upstox_streamer = streamer
        def on_open():
            broadcast({'type':'status','status':'connected','source':'upstox'})
        def on_close(*args):
            global upstox_streamer
            with upstox_streamer_lock:
                upstox_streamer = None
            broadcast({'type':'status','status':'disconnected','source':'upstox'})
        def on_error(*args):
            broadcast({'type':'status','status':'error','source':'upstox'})
        def on_message(message):
            feeds = message.get('feeds', {}) if isinstance(message, dict) else {}
            for instrument_key, feed in feeds.items():
                ltpc = (feed or {}).get('ltpc', {})
                ltp = ltpc.get('ltp')
                cp = ltpc.get('cp')
                if ltp is None:
                    continue
                symbol = next((k for k,v in instrument_catalog.items() if v.get('instrument_key') == instrument_key), instrument_key.split('|')[-1])
                if symbol not in instrument_catalog and instrument_key in INSTRUMENT_KEYS.values():
                    symbol = next(k for k,v in INSTRUMENT_KEYS.items() if v == instrument_key)
                change = ((float(ltp)-float(cp))/float(cp)*100) if cp else 0.0
                set_tick(symbol, float(ltp), change, int(ltpc.get('ltt') or time.time()*1000))
                broadcast({'type':'tick', **state[symbol]})
        streamer.on('open', on_open)
        streamer.on('close', on_close)
        streamer.on('error', on_error)
        streamer.on('message', on_message)
        streamer.auto_reconnect(True, 5, 100)
        streamer.connect()
    except Exception as exc:
        broadcast({'type':'status','status':'error','source':'upstox','message':str(exc)})

def simulator_worker():
    rnd = random.Random(7)
    while True:
        time.sleep(1.5)
        if UPSTOX_ACCESS_TOKEN and not USE_SIMULATOR:
            return
        for symbol in list(state):
            old = state[symbol]['price']
            change = state[symbol]['change'] + (rnd.random()-.5)*.25
            price = max(.5, old*(1+change/10000))
            set_tick(symbol, price, change, int(time.time()*1000))
            state[symbol]['source'] = 'simulator'
            broadcast({'type':'tick', **state[symbol]})

def subscribe_upstox_symbols(symbols: list[str]):
    if not UPSTOX_ACCESS_TOKEN:
        return
    keys = []
    for symbol in symbols:
        item = instrument_catalog.get(normalize_symbol(symbol))
        if item and item.get('instrument_key'):
            keys.append(item['instrument_key'])
        elif normalize_symbol(symbol) in INSTRUMENT_KEYS:
            keys.append(INSTRUMENT_KEYS[normalize_symbol(symbol)])
    if not keys:
        return
    with upstox_streamer_lock:
        streamer = upstox_streamer
    if streamer:
        try:
            streamer.subscribe(sorted(set(keys)), 'ltpc')
        except Exception as exc:
            print(f'Upstox subscribe failed: {exc}')

app = FastAPI(title='InvestEdge Unified Backend', version='2.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.on_event('startup')
async def startup():
    global loop, upstox_thread
    loop = asyncio.get_running_loop()
    if UPSTOX_ACCESS_TOKEN:
        upstox_thread = threading.Thread(target=upstox_worker, daemon=True)
        upstox_thread.start()
    elif USE_SIMULATOR:
        threading.Thread(target=simulator_worker, daemon=True).start()

@app.get('/health')
def health():
    return {'status':'ok','environment':APP_ENV,'market_source':'upstox' if UPSTOX_ACCESS_TOKEN else 'simulator','ai_configured':bool(AI_API_KEY)}

@app.get('/api/state')
def snapshot():
    return {'source':'upstox' if UPSTOX_ACCESS_TOKEN else 'simulator','stocks':list(state.values())}

@app.post('/auth/register')
def register(body: LoginBody):
    email = body.email.strip().lower()
    if len(body.password) < 8:
        raise HTTPException(400, 'Password must be at least 8 characters')
    try:
        con.execute('INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)',(email,pw_hash(body.password),datetime.now(timezone.utc).isoformat()))
        con.commit()
        uid = con.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()['id']
        for s in DEFAULT_SYMBOLS: con.execute('INSERT OR IGNORE INTO watchlist(user_id,symbol) VALUES(?,?)',(uid,s))
        con.commit()
        return {'token':token_for(uid),'email':email}
    except sqlite3.IntegrityError:
        raise HTTPException(409, 'Account already exists')

@app.post('/auth/login')
def login(body: LoginBody):
    row = con.execute('SELECT * FROM users WHERE email=?',(body.email.strip().lower(),)).fetchone()
    if not row or not pw_ok(body.password,row['password_hash']):
        raise HTTPException(401,'Invalid credentials')
    return {'token':token_for(row['id']),'email':row['email']}

@app.get('/api/watchlist')
def get_watchlist(token: str):
    uid = user_id_from_token(token)
    return {'symbols':[r['symbol'] for r in con.execute('SELECT symbol FROM watchlist WHERE user_id=? ORDER BY symbol',(uid,)).fetchall()]}

@app.post('/api/watchlist')
def add_watchlist(body: WatchBody, token: str):
    uid = user_id_from_token(token); sym=normalize_symbol(body.symbol)
    con.execute('INSERT OR IGNORE INTO watchlist(user_id,symbol) VALUES(?,?)',(uid,sym)); con.commit()
    return {'ok':True,'symbol':sym}

@app.delete('/api/watchlist/{symbol}')
def remove_watchlist(symbol: str, token: str):
    uid=user_id_from_token(token); con.execute('DELETE FROM watchlist WHERE user_id=? AND symbol=?',(uid,normalize_symbol(symbol))); con.commit(); return {'ok':True}

@app.get('/api/portfolio')
def get_portfolio(token: str):
    uid=user_id_from_token(token)
    return {'holdings':[dict(r) for r in con.execute('SELECT symbol,qty,avg_price FROM holdings WHERE user_id=?',(uid,)).fetchall()]}

@app.post('/api/portfolio')
def save_holding(body: HoldingBody, token: str):
    uid=user_id_from_token(token); sym=normalize_symbol(body.symbol)
    con.execute('INSERT INTO holdings(user_id,symbol,qty,avg_price) VALUES(?,?,?,?) ON CONFLICT(user_id,symbol) DO UPDATE SET qty=excluded.qty,avg_price=excluded.avg_price',(uid,sym,body.qty,body.avg_price)); con.commit(); return {'ok':True}

@app.get('/api/signal/{symbol}')
def signal(symbol: str):
    sym=normalize_symbol(symbol)
    if sym not in state:
        base=100.0; set_tick(sym,base,0)
    return state[sym]

@app.post('/api/ai/insight')
async def ai_insight(payload: dict[str, Any]):
    symbol=normalize_symbol(str(payload.get('symbol','')))
    stock=state.get(symbol)
    if not stock: raise HTTPException(404,'Symbol not available')
    fallback=f"{stock['signal']} bias with confidence {stock['confidence']:.1f}%. Technical {stock['technical']:.0f}/100, fundamental {stock['fundamental']:.0f}/100, momentum {stock['momentum']:.0f}/100 and risk {stock['risk']:.0f}/100. This is an analytical signal, not a guaranteed outcome."
    if not AI_API_KEY: return {'source':'rule-engine','insight':fallback}
    headers={'Authorization':f'Bearer {AI_API_KEY}','Content-Type':'application/json'}
    body={'model':AI_MODEL,'messages':[{'role':'system','content':'You are InvestEdge, a market-research assistant. Give concise, non-guaranteed analytical insight; do not execute trades.'},{'role':'user','content':json.dumps(stock)}],'temperature':0.2}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r=await client.post(f'{AI_BASE_URL.rstrip("/")}/chat/completions',headers=headers,json=body); r.raise_for_status(); data=r.json()
        return {'source':'ai','insight':data['choices'][0]['message']['content']}
    except Exception:
        return {'source':'rule-engine','insight':fallback}

@app.websocket('/ws/market')
async def market_ws(ws: WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        await ws.send_json({'type':'status','status':'connected','source':'upstox' if UPSTOX_ACCESS_TOKEN else 'simulator'})
        await ws.send_json({'type':'catalog','stocks':list(instrument_catalog.values())})
        for item in state.values(): await ws.send_json({'type':'tick',**item})
        while True:
            msg=await ws.receive_json()
            if msg.get('action') == 'subscribe':
                symbols = [str(x) for x in (msg.get('symbols') or [])]
                subscribe_upstox_symbols(symbols)
                await ws.send_json({'type':'subscription','symbols':symbols,'status':'accepted'})
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
