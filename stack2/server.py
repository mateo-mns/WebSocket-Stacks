# server.py
import asyncio
import json
import uuid
import logging
import os
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)

# Estado en memoria (SIMPLE)
SESSIONS = {}     # token -> username
CONNECTED = set() # conjunto de WebSocketResponse activos

# RUTAS HTTP
async def index(request):
    return web.FileResponse('./static/index.html')

async def login(request):
    # POST JSON { "username": "..." }
    try:
        data = await request.json()
    except Exception:
        return web.json_response({'ok': False, 'error': 'json required'}, status=400)

    username = (data.get('username') or '').strip()
    if not username:
        return web.json_response({'ok': False, 'error': 'username required'}, status=400)

    token = uuid.uuid4().hex
    SESSIONS[token] = username
    resp = web.json_response({'ok': True, 'username': username})
    # Cookie simple (en producción usar secure=True)
    resp.set_cookie('session', token, httponly=True, samesite='Lax')
    logging.info("User logged in: %s (token %s)", username, token[:8])
    return resp

async def whoami(request):
    token = request.cookies.get('session')
    if not token or token not in SESSIONS:
        return web.json_response({'ok': False, 'error': 'no session'}, status=401)
    return web.json_response({'ok': True, 'username': SESSIONS[token]})

# WEBSOCKET
async def websocket_handler(request):
    token = request.cookies.get('session')
    if not token or token not in SESSIONS:
        raise web.HTTPUnauthorized(reason='session missing or invalid')

    username = SESSIONS[token]
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    CONNECTED.add(ws)
    logging.info("%s connected (local connections=%d)", username, len(CONNECTED))
    await ws.send_json({'type':'system','text':f'Conectado como {username}'})

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    payload = json.loads(msg.data)
                except Exception:
                    await ws.send_json({'type':'error','text':'invalid json'})
                    continue

                if payload.get('type') == 'chat':
                    text = str(payload.get('text',''))[:1000]
                    # broadcast simple en memoria
                    message = {'type':'chat','from': username, 'text': text}
                    await broadcast(message)
                else:
                    await ws.send_json({'type':'error','text':'unknown type'})
            elif msg.type == WSMsgType.ERROR:
                logging.error('ws exception %s', ws.exception())
    finally:
        CONNECTED.discard(ws)
        logging.info("%s disconnected (local connections=%d)", username, len(CONNECTED))

    return ws

# UTIL: broadcast a clientes locales
async def broadcast(message):
    text = json.dumps(message)
    to_remove = []
    for ws in list(CONNECTED):
        try:
            await ws.send_str(text)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        CONNECTED.discard(ws)

# BACKGROUND: heartbeat opcional (mantener vivo)
async def heartbeat(app):
    try:
        while True:
            await asyncio.sleep(30)
            if CONNECTED:
                await broadcast({'type':'system','text':'heartbeat'})
    except asyncio.CancelledError:
        logging.info('heartbeat cancelled')
        raise

async def start_background(app):
    app['hb'] = asyncio.create_task(heartbeat(app))
    logging.info('background started')

async def cleanup_background(app):
    t = app.pop('hb', None)
    if t:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
    logging.info('background cleaned')

def create_app():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/login', login)
    app.router.add_get('/whoami', whoami)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/static/', path='./static', name='static')

    app.on_startup.append(start_background)
    app.on_cleanup.append(cleanup_background)
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(create_app(), host='0.0.0.0', port=port)
