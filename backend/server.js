const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { Store } = require('./store');
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config/gameplay.json')));
const port = Number(process.env.PORT || 8080);
const store = new Store(process.env.BHC_DATA_FILE || path.join(__dirname, 'data/state.json'), config);
const json = (res, code, body) => { res.writeHead(code, { 'content-type': 'application/json', 'cache-control': 'no-store' }); res.end(JSON.stringify(body)); };
const body = req => new Promise((resolve, reject) => { let s = ''; req.on('data', c => { s += c; if (s.length > 100_000) reject(new Error('body too large')); }); req.on('end', () => { try { resolve(s ? JSON.parse(s) : {}); } catch { reject(new Error('invalid JSON')); } }); });
const fail = (res, e) => json(res, /capacity|full/.test(e.message) ? 409 : 400, { error: e.message });
const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/') { res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); return res.end(fs.readFileSync(path.join(__dirname, '../web/index.html'))); }
    if (req.method === 'GET' && req.url === '/api/config') return json(res, 200, config);
    if (req.method !== 'POST') return json(res, 404, { error: 'not found' });
    const data = await body(req);
    if (req.url === '/api/crews') return json(res, 201, store.createCrew(data.accountId));
    if (req.url === '/api/crews/join') return json(res, 200, store.joinCrew(data.crewId, data.accountId));
    if (req.url === '/api/reservations') return json(res, 201, store.reserve(data.crewId, data.region || 'us-west'));
    if (req.url === '/api/sessions') return json(res, 201, store.bindSession(data.reservationId, data.accountId));
    if (req.url === '/api/sessions/validate') return json(res, 200, { valid: !!store.authenticate(data.token) });
    if (req.url === '/api/world/vehicle') return json(res, 201, store.spawnStarterVehicle(data.crewId, data.accountId));
    if (req.url === '/api/world/vehicle/board') return json(res, 200, store.boardVehicle(data.vehicleId, data.accountId));
    if (req.url === '/api/world/position') return json(res, 200, store.updateWorldPosition(data.accountId, data.destination));
    if (req.url === '/api/world/reconnect-position') return json(res, 200, { destination: store.reconnectPosition(data.accountId) });
    return json(res, 404, { error: 'not found' });
  } catch (e) { return fail(res, e); }
});
if (require.main === module) server.listen(port, () => console.log(`Big Head Casino backend listening on http://localhost:${port}`));
module.exports = { server, store };
