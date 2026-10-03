const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { Store } = require('../store');
const config = require('../config/gameplay.json');
function make() { return new Store(path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'bhc-')), 'state.json'), config); }
test('crew reservations enforce four-player crews and bind sessions', () => { const s = make(); const c = s.createCrew('a'); s.joinCrew(c.id, 'b'); s.joinCrew(c.id, 'c'); s.joinCrew(c.id, 'd'); assert.throws(() => s.joinCrew(c.id, 'e'), /full/); const r = s.reserve(c.id, 'us-west'); const session = s.bindSession(r.id, 'b'); assert.equal(s.authenticate(session.token).accountId, 'b'); assert.throws(() => s.bindSession(r.id, 'e'), /not in crew/); });
test('lobby reservations cannot exceed 100 players', () => { const s = make(); for (let i = 0; i < 25; i++) { const c = s.createCrew(`p${i}`); for (let j = 1; j < 4; j++) s.joinCrew(c.id, `p${i}-${j}`); s.reserve(c.id, 'us-west'); } const extra = s.createCrew('overflow'); s.joinCrew(extra.id, 'overflow-1'); s.joinCrew(extra.id, 'overflow-2'); s.joinCrew(extra.id, 'overflow-3'); assert.throws(() => s.reserve(extra.id, 'us-west'), /capacity/); });
test('crew vehicle seats and safe reconnect position are authoritative', () => { const s = make(); const c = s.createCrew('driver'); s.joinCrew(c.id, 'passenger'); const v = s.spawnStarterVehicle(c.id, 'driver'); s.boardVehicle(v.id, 'driver'); s.boardVehicle(v.id, 'passenger'); assert.equal(v.occupants.length, 2); s.updateWorldPosition('driver', 'grand_casino'); assert.equal(s.reconnectPosition('driver'), 'grand_casino'); assert.throws(() => s.updateWorldPosition('driver', 'unbuilt_building'), /not playable/); });
