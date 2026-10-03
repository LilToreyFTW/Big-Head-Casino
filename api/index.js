const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const state = globalThis.__bhcState || (globalThis.__bhcState = { crews: new Map(), vehicles: new Map(), accounts: new Map() });
const destinations = [
  ['arrival_plaza', 'Arrival Plaza', true], ['casino_strip', 'Casino Strip', true],
  ['grand_casino', 'The Grand Casino', true], ['equipment_shop', 'Equipment Shop', true],
  ['crew_garage', 'Crew Garage', true], ['service_district', 'Service District', true],
  ['rooftop_overlook', 'Rooftop Overlook', true]
];
const id = p => `${p}_${crypto.randomBytes(6).toString('hex')}`;
const send = (res, status, value, type = 'application/json') => { res.statusCode = status; res.setHeader('content-type', type); res.setHeader('cache-control', 'no-store'); res.end(type === 'application/json' ? JSON.stringify(value) : value); };
const readBody = req => new Promise((resolve, reject) => { let text = ''; req.on('data', c => { text += c; if (text.length > 100000) reject(new Error('body too large')); }); req.on('end', () => { try { resolve(text ? JSON.parse(text) : {}); } catch { reject(new Error('invalid JSON')); } }); });

module.exports = async (req, res) => {
  try {
    if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) return send(res, 200, fs.readFileSync(path.join(process.cwd(), 'web/index.html'), 'utf8'), 'text/html; charset=utf-8');
    if (req.method === 'GET' && req.url === '/api/config') return send(res, 200, { lobby: { maxPlayers: 100, maxCrewSize: 4 }, vehicle: { assetId: 'BHC_VEH_CREW_VAN', seats: 4 }, destinations: destinations.map(([id, name, playable]) => ({ id, name, playable })) });
    if (req.method !== 'POST') return send(res, 404, { error: 'not found' });
    const body = await readBody(req);
    if (req.url === '/api/crews') { if (!body.accountId) throw Error('accountId is required'); const crew = { id: id('crew'), leaderId: body.accountId, members: [body.accountId] }; state.crews.set(crew.id, crew); return send(res, 201, crew); }
    if (req.url === '/api/crews/join') { const crew = state.crews.get(body.crewId); if (!crew) throw Error('crew not found'); if (!crew.members.includes(body.accountId) && crew.members.length >= 4) throw Error('crew is full'); if (!crew.members.includes(body.accountId)) crew.members.push(body.accountId); return send(res, 200, crew); }
    if (req.url === '/api/world/vehicle') { const crew = state.crews.get(body.crewId); if (!crew || crew.leaderId !== body.accountId) throw Error('only the crew leader may spawn the vehicle'); const vehicle = { id: id('veh'), crewId: body.crewId, assetId: 'BHC_VEH_CREW_VAN', seats: 4, occupants: [], condition: 100, destination: 'crew_garage' }; state.vehicles.set(vehicle.id, vehicle); return send(res, 201, vehicle); }
    if (req.url === '/api/world/vehicle/board') { const vehicle = state.vehicles.get(body.vehicleId); if (!vehicle) throw Error('vehicle not found'); const crew = state.crews.get(vehicle.crewId); if (!crew.members.includes(body.accountId)) throw Error('account is not in crew'); if (vehicle.occupants.length >= vehicle.seats && !vehicle.occupants.includes(body.accountId)) throw Error('vehicle is full'); if (!vehicle.occupants.includes(body.accountId)) vehicle.occupants.push(body.accountId); return send(res, 200, vehicle); }
    if (req.url === '/api/world/position') { if (!destinations.some(d => d[0] === body.destination && d[2])) throw Error('destination is not playable'); return send(res, 200, { accountId: body.accountId, destination: body.destination }); }
    return send(res, 404, { error: 'not found' });
  } catch (error) { return send(res, 400, { error: error.message }); }
};
