"""InvestEdge backend: secure-by-default API and market WebSocket.

Production note: real market data requires a valid Upstox access token and a verified
provider connection. No synthetic prices are ever labelled as live.
"""
from __future__ import annotations
import asyncio, hashlib, hmac, json, logging, os, secrets, sqlite3, threading, time, gzip
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx, jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'))
log = logging.getLogger('investedge')
APP_ENV = os.getenv('APP_ENV','development').lower()
JWT_SECRET = os.getenv('JWT_SECRET','')
DATABASE_URL = os.getenv('DATABASE_URL','data/investedge.db')
AI_API_KEY = os.getenv('AI_API_KEY','')
AI_BASE_URL = os.getenv('AI_BASE_URL','https://api.deepseek.com/v1').rstrip('/')
AI_MODEL = os.getenv('AI_MODEL','deepseek-chat')
UPSTOX_ACCESS_TOKEN = os.getenv('UPSTOX_ACCESS_TOKEN','')
NSE_INSTRUMENTS_URL = os.getenv('NSE_INSTRUMENTS_URL','https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz')
USE_SIMULATOR = os.getenv('USE_SIMULATOR','true').lower() == 'true'
ALLOWED_ORIGINS = [x.strip() for x in os.getenv('ALLOWED_ORIGINS','http://localhost:62073,http://127.0.0.1:62073').split(',') if x.strip()]
TOKEN_TTL_SECONDS = int(os.getenv('TOKEN_TTL_SECONDS','3600'))
MAX_WS_CLIENTS = int(os.getenv('MAX_WS_CLIENTS','200'))

if APP_ENV == 'production':
    if len(JWT_SECRET) < 32:
        raise RuntimeError('Production requires JWT_SECRET with at least 32 characters.')
    if USE_SIMULATOR:
        raise RuntimeError('USE_SIMULATOR must be false in production. Refusing to serve simulated data.')
    if '*' in ALLOWED_ORIGINS:
        raise RuntimeError('Wildcard CORS is forbidden in production; set ALLOWED_ORIGINS explicitly.')
else:
    JWT_SECRET = JWT_SECRET or 'local-development-only-secret-change-before-deploy-9f73'

Path(DATABASE_URL).parent.mkdir(parents=True, exist_ok=True)
DB_LOCK = threading.RLock()
STATE_LOCK = threading.RLock()
state: dict[str, dict[str, Any]] = {}
clients: set[WebSocket] = set()
clients_lock = asyncio.Lock()
loop: asyncio.AbstractEventLoop | None = None
upstox_streamer = None
upstox_streamer_lock = threading.Lock()
stream_status = {'status':'disabled' if not UPSTOX_ACCESS_TOKEN else 'starting', 'source':'upstox' if UPSTOX_ACCESS_TOKEN else 'none', 'last_message_at':None, 'last_error':None}
DEFAULT_SYMBOLS = ['RELIANCE','TCS','HDFCBANK','ICICIBANK','INFY','ITC','AXISBANK','SBIN']
INSTRUMENT_KEYS = {'RELIANCE':'NSE_EQ|INE002A01018','TCS':'NSE_EQ|INE467B01029','HDFCBANK':'NSE_EQ|INE040A01034','ICICIBANK':'NSE_EQ|INE090A01021','INFY':'NSE_EQ|INE009A01021','ITC':'NSE_EQ|INE154A01025','AXISBANK':'NSE_EQ|INE238A01034','SBIN':'NSE_EQ|INE062A01020'}
instrument_catalog: dict[str, dict[str,str]] = {s:{'symbol':s,'name':s,'instrument_key':INSTRUMENT_KEYS[s]} for s in DEFAULT_SYMBOLS}

# SQLite connection per operation avoids sharing one connection unsafely between request threads.
def db_connect():
    con = sqlite3.connect(DATABASE_URL, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA busy_timeout=15000')
    return con

def init_db():
    with DB_LOCK, db_connect() as con:
        con.execute('PRAGMA journal_mode=WAL')
        con.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS watchlist(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, symbol TEXT NOT NULL, UNIQUE(user_id,symbol));
        CREATE TABLE IF NOT EXISTS holdings(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, symbol TEXT NOT NULL, qty REAL NOT NULL CHECK(qty >= 0), avg_price REAL NOT NULL CHECK(avg_price >= 0), UNIQUE(user_id,symbol));
        ''')
init_db()

def normalize_symbol(s: str) -> str:
    return ''.join(s.upper().split())

def signal_for(price: float, change: float) -> dict[str, float | str]:
    # Explicitly heuristic, not investment advice or a validated prediction model.
    momentum = max(0.0, min(100.0, 50 + change * 10))
    technical = max(0.0, min(100.0, 58 + change * 12))
    fundamental = 50.0  # Unknown until sourced fundamentals are connected.
    risk = max(10.0, min(95.0, 58 - abs(change) * 6))
    score = technical*.35 + fundamental*.30 + momentum*.20 + risk*.15
    signal = 'BUY' if score >= 68 else 'SELL' if score <= 43 else 'HOLD'
    confidence = max(0.0, min(100.0, 50 + abs(score-50)*1.25))
    return {'technical':round(technical,2),'fundamental':fundamental,'momentum':round(momentum,2),'risk':round(risk,2),'score':round(score,2),'signal':signal,'confidence':round(confidence,2)}

def set_tick(symbol: str, price: float, change: float, updated_ms: int | None = None, source: str = 'upstox'):
    if price <= 0 or not (price < float('inf')) or not (-1000 < change < 1000):
        return
    metrics = signal_for(price, change)
    tick = {'symbol':symbol,'price':round(price,4),'change':round(change,4),'rsi':None,**metrics,'updated':updated_ms or int(time.time()*1000),'source':source}
    with STATE_LOCK: state[symbol] = tick

def load_nse_catalog():
    global instrument_catalog
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(NSE_INSTRUMENTS_URL); r.raise_for_status()
            raw = gzip.decompress(r.content) if r.content[:2] == b'\x1f\x8b' else r.content
        rows = json.loads(raw.decode('utf-8')); catalog = {}
        for item in rows:
            if item.get('segment') != 'NSE_EQ' or item.get('instrument_type') not in ('EQ','BE'): continue
            symbol = str(item.get('trading_symbol') or '').strip().upper()
            key = str(item.get('instrument_key') or '')
            if symbol and key: catalog[symbol] = {'symbol':symbol,'name':str(item.get('short_name') or item.get('name') or symbol),'instrument_key':key}
        if catalog: instrument_catalog = catalog; log.info('Loaded %s NSE instruments',len(catalog))
    except Exception as exc:
        log.warning('Instrument catalogue refresh failed; using limited built-in list: %s',type(exc).__name__)
load_nse_catalog()

class Credentials(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class HoldingBody(BaseModel):
    symbol: str = Field(min_length=1,max_length=30)
    qty: float = Field(ge=0, le=1e12, allow_inf_nan=False)
    avg_price: float = Field(ge=0, le=1e12, allow_inf_nan=False)
class WatchBody(BaseModel):
    symbol: str = Field(min_length=1,max_length=30)
class InsightBody(BaseModel):
    symbol: str = Field(min_length=1,max_length=30)


def pw_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    return f'{salt}${hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),310_000).hex()}'
def pw_ok(password: str, encoded: str) -> bool:
    try:
        salt, digest = encoded.split('$',1)
        check = hashlib.pbkdf2_hmac('sha256',password.encode(),salt.encode(),310_000).hex()
        return hmac.compare_digest(check,digest)
    except Exception: return False
def token_for(user_id: int) -> str:
    return jwt.encode({'sub':str(user_id),'iat':int(time.time()),'exp':int(time.time())+TOKEN_TTL_SECONDS},JWT_SECRET,algorithm='HS256')
def user_id_from_token(token: str) -> int:
    try: return int(jwt.decode(token,JWT_SECRET,algorithms=['HS256'],options={'require':['sub','iat','exp']})['sub'])
    except Exception: raise HTTPException(401,'Invalid or expired token')
def current_user(authorization: str | None = Header(default=None), token: str | None = Query(default=None)) -> int:
    # Query-token fallback preserves compatibility with the current Flutter WebSocket/API integration;
    # new clients should use Authorization: Bearer <token>.
    raw = token
    if authorization:
        scheme, _, value = authorization.partition(' ')
        if scheme.lower() != 'bearer' or not value: raise HTTPException(401,'Use Bearer authentication')
        raw = value
    if not raw: raise HTTPException(401,'Authentication required')
    return user_id_from_token(raw)

async def broadcast(payload: dict[str,Any]):
    async with clients_lock:
        current = list(clients)
    dead=[]
    for ws in current:
        try: await ws.send_json(payload)
        except Exception: dead.append(ws)
    if dead:
        async with clients_lock:
            for ws in dead: clients.discard(ws)

def broadcast_from_thread(payload):
    if loop and not loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast(payload),loop)

def upstox_worker():
    global upstox_streamer
    try:
        import upstox_client
        config=upstox_client.Configuration(); config.access_token=UPSTOX_ACCESS_TOKEN
        keys=list(dict.fromkeys(v['instrument_key'] for v in instrument_catalog.values() if v.get('instrument_key')))
        if not keys: keys=list(INSTRUMENT_KEYS.values())
        streamer=upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(config),keys,'ltpc')
        with upstox_streamer_lock: upstox_streamer=streamer
        def on_open(*args):
            stream_status.update(status='connected',last_error=None); broadcast_from_thread({'type':'status','status':'connected','source':'upstox'})
        def on_close(*args):
            with upstox_streamer_lock: globals()['upstox_streamer']=None
            stream_status.update(status='disconnected'); broadcast_from_thread({'type':'status','status':'disconnected','source':'upstox'})
        def on_error(*args):
            stream_status.update(status='error',last_error='Provider stream error'); broadcast_from_thread({'type':'status','status':'error','source':'upstox'})
        def on_message(message):
            try:
                feeds=message.get('feeds',{}) if isinstance(message,dict) else {}
                for key,feed in feeds.items():
                    ltpc=(feed or {}).get('ltpc',{}); ltp=ltpc.get('ltp'); cp=ltpc.get('cp')
                    if ltp is None: continue
                    symbol=next((k for k,v in instrument_catalog.items() if v.get('instrument_key')==key),None)
                    if not symbol: symbol=next((k for k,v in INSTRUMENT_KEYS.items() if v==key),None)
                    if not symbol: continue
                    change=(float(ltp)-float(cp))/float(cp)*100 if cp else 0.0
                    set_tick(symbol,float(ltp),change,int(ltpc.get('ltt') or time.time()*1000),'upstox')
                    stream_status.update(last_message_at=datetime.now(timezone.utc).isoformat())
                    with STATE_LOCK: tick=state[symbol].copy()
                    broadcast_from_thread({'type':'tick',**tick})
            except Exception: log.exception('Could not process market message')
        streamer.on('open',on_open); streamer.on('close',on_close); streamer.on('error',on_error); streamer.on('message',on_message)
        streamer.auto_reconnect(True,5,100); streamer.connect()
    except Exception as exc:
        stream_status.update(status='error',last_error=type(exc).__name__)
        log.exception('Upstox stream failed')
        broadcast_from_thread({'type':'status','status':'error','source':'upstox'})

def simulator_worker():
    # Development-only visual demo. It is impossible to enable in APP_ENV=production.
    import random
    rnd=random.Random()
    for sym in DEFAULT_SYMBOLS: set_tick(sym,100+rnd.random()*1000,0,source='simulator')
    while True:
        time.sleep(2)
        with STATE_LOCK: snapshot=[(s,x.copy()) for s,x in state.items() if x.get('source')=='simulator']
        for symbol,tick in snapshot:
            price=tick['price']*(1+(rnd.random()-.5)*.001)
            change=tick['change']+(rnd.random()-.5)*.2
            set_tick(symbol,price,change,source='simulator')
            with STATE_LOCK: updated=state[symbol].copy()
            broadcast_from_thread({'type':'tick',**updated})

def subscribe_upstox_symbols(symbols: list[str]):
    if not UPSTOX_ACCESS_TOKEN: return
    keys=[instrument_catalog[s]['instrument_key'] for s in map(normalize_symbol,symbols) if s in instrument_catalog]
    with upstox_streamer_lock: streamer=upstox_streamer
    if streamer and keys:
        try: streamer.subscribe(list(set(keys)),'ltpc')
        except Exception: log.exception('Upstox subscription failed')

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop=asyncio.get_running_loop()
    if UPSTOX_ACCESS_TOKEN:
        threading.Thread(target=upstox_worker,daemon=True,name='upstox-stream').start()
    elif USE_SIMULATOR and APP_ENV != 'production':
        threading.Thread(target=simulator_worker,daemon=True,name='market-simulator').start()
    elif APP_ENV == 'production':
        log.warning('No Upstox token configured: market feed is unavailable, not live.')
    yield
    loop=None

app=FastAPI(title='InvestEdge API',version='3.0.0',lifespan=lifespan,docs_url='/docs' if APP_ENV!='production' else None,redoc_url=None)
app.add_middleware(CORSMiddleware,allow_origins=ALLOWED_ORIGINS,allow_credentials=False,allow_methods=['GET','POST','DELETE','OPTIONS'],allow_headers=['Authorization','Content-Type'])

@app.get('/health')
def health():
    live=stream_status['status']=='connected' and (time.time() - (datetime.fromisoformat(stream_status['last_message_at']).timestamp() if stream_status['last_message_at'] else 0) < 90)
    return {'status':'ok','environment':APP_ENV,'market':{'status':stream_status['status'],'source':stream_status['source'],'live':live,'last_message_at':stream_status['last_message_at']},'ai_configured':bool(AI_API_KEY)}
@app.get('/api/state')
def snapshot():
    with STATE_LOCK: stocks=[v.copy() for v in state.values()]
    return {'source':stream_status['source'],'status':stream_status['status'],'stocks':stocks}
@app.post('/auth/register')
def register(body: Credentials):
    email=str(body.email).lower()
    if len(body.password)<10: raise HTTPException(400,'Password must be at least 10 characters')
    try:
        with DB_LOCK,db_connect() as con:
            cur=con.execute('INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)',(email,pw_hash(body.password),datetime.now(timezone.utc).isoformat()))
            uid=cur.lastrowid
            con.executemany('INSERT OR IGNORE INTO watchlist(user_id,symbol) VALUES(?,?)',[(uid,s) for s in DEFAULT_SYMBOLS])
        return {'token':token_for(uid),'email':email,'token_type':'bearer','expires_in':TOKEN_TTL_SECONDS}
    except sqlite3.IntegrityError: raise HTTPException(409,'Account already exists')
@app.post('/auth/login')
def login(body: Credentials):
    with DB_LOCK,db_connect() as con: row=con.execute('SELECT * FROM users WHERE email=?',(str(body.email).lower(),)).fetchone()
    if not row or not pw_ok(body.password,row['password_hash']): raise HTTPException(401,'Invalid credentials')
    return {'token':token_for(row['id']),'email':row['email'],'token_type':'bearer','expires_in':TOKEN_TTL_SECONDS}
@app.get('/api/watchlist')
def get_watchlist(uid: int=Depends(current_user)):
    with DB_LOCK,db_connect() as con: rows=con.execute('SELECT symbol FROM watchlist WHERE user_id=? ORDER BY symbol',(uid,)).fetchall()
    return {'symbols':[r['symbol'] for r in rows]}
@app.post('/api/watchlist')
def add_watchlist(body: WatchBody,uid: int=Depends(current_user)):
    sym=normalize_symbol(body.symbol)
    with DB_LOCK,db_connect() as con: con.execute('INSERT OR IGNORE INTO watchlist(user_id,symbol) VALUES(?,?)',(uid,sym))
    return {'ok':True,'symbol':sym}
@app.delete('/api/watchlist/{symbol}')
def remove_watchlist(symbol: str,uid: int=Depends(current_user)):
    with DB_LOCK,db_connect() as con: con.execute('DELETE FROM watchlist WHERE user_id=? AND symbol=?',(uid,normalize_symbol(symbol)))
    return {'ok':True}
@app.get('/api/portfolio')
def get_portfolio(uid: int=Depends(current_user)):
    with DB_LOCK,db_connect() as con: rows=con.execute('SELECT symbol,qty,avg_price FROM holdings WHERE user_id=?',(uid,)).fetchall()
    return {'holdings':[dict(r) for r in rows]}
@app.post('/api/portfolio')
def save_holding(body: HoldingBody,uid: int=Depends(current_user)):
    sym=normalize_symbol(body.symbol)
    with DB_LOCK,db_connect() as con: con.execute('INSERT INTO holdings(user_id,symbol,qty,avg_price) VALUES(?,?,?,?) ON CONFLICT(user_id,symbol) DO UPDATE SET qty=excluded.qty,avg_price=excluded.avg_price',(uid,sym,body.qty,body.avg_price))
    return {'ok':True,'symbol':sym}
@app.get('/api/signal/{symbol}')
def signal(symbol: str):
    sym=normalize_symbol(symbol)
    with STATE_LOCK: item=state.get(sym)
    if not item: raise HTTPException(404,'No market data for symbol. Verify the provider subscription and market hours.')
    return item
@app.post('/api/ai/insight')
async def ai_insight(payload: InsightBody,uid: int=Depends(current_user)):
    sym=normalize_symbol(payload.symbol)
    with STATE_LOCK: stock=state.get(sym)
    if not stock: raise HTTPException(404,'No market data available for symbol')
    fallback=f"Heuristic score {stock['score']}/100; technical {stock['technical']}/100, fundamentals unavailable, momentum {stock['momentum']}/100, risk indicator {stock['risk']}/100. This is general research, not a recommendation or guarantee."
    if not AI_API_KEY: return {'source':'rule-engine','insight':fallback,'disclaimer':'Not financial advice.'}
    headers={'Authorization':f'Bearer {AI_API_KEY}','Content-Type':'application/json'}
    req={'model':AI_MODEL,'messages':[{'role':'system','content':'You provide cautious educational market research, distinguish facts from uncertainty, do not guarantee returns or execute trades. State that this is not financial advice.'},{'role':'user','content':json.dumps(stock)}],'temperature':0.2}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r=await client.post(f'{AI_BASE_URL}/chat/completions',headers=headers,json=req); r.raise_for_status(); data=r.json()
        answer=data['choices'][0]['message']['content']
        return {'source':'ai','insight':answer,'disclaimer':'Not financial advice.'}
    except Exception as exc:
        log.warning('AI provider failed: %s',type(exc).__name__)
        return {'source':'rule-engine','insight':fallback,'disclaimer':'Not financial advice.'}
@app.websocket('/ws/market')
async def market_ws(ws: WebSocket):
    # Public market ticks only. Account-specific messages are not accepted here.
    await ws.accept()
    async with clients_lock:
        if len(clients)>=MAX_WS_CLIENTS:
            await ws.close(code=1013,reason='Server at capacity'); return
        clients.add(ws)
    try:
        await ws.send_json({'type':'status','status':stream_status['status'],'source':stream_status['source']})
        await ws.send_json({'type':'catalog','stocks':list(instrument_catalog.values())})
        with STATE_LOCK: initial=[v.copy() for v in state.values()]
        for item in initial: await ws.send_json({'type':'tick',**item})
        while True:
            try: msg=await asyncio.wait_for(ws.receive_json(),timeout=60)
            except asyncio.TimeoutError:
                await ws.send_json({'type':'ping','at':int(time.time()*1000)}); continue
            if isinstance(msg,dict) and msg.get('action')=='subscribe':
                symbols=[normalize_symbol(str(x))[:30] for x in (msg.get('symbols') or [])[:50]]
                subscribe_upstox_symbols(symbols)
                await ws.send_json({'type':'subscription','symbols':symbols,'status':'accepted' if UPSTOX_ACCESS_TOKEN else 'unavailable','source':stream_status['source']})
    except (WebSocketDisconnect,RuntimeError): pass
    finally:
        async with clients_lock: clients.discard(ws)
