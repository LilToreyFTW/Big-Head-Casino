const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

function id(prefix) { return `${prefix}_${crypto.randomBytes(8).toString('hex')}`; }

class Store {
  constructor(file, config) {
    this.file = file;
    this.config = config;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    this.state = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : { accounts: {}, crews: {}, lobbies: {}, reservations: {}, sessions: {}, vehicles: {}, worldProgress: {}, audit: [] };
  }
  save() { const tmp = `${this.file}.tmp`; fs.writeFileSync(tmp, JSON.stringify(this.state, null, 2)); fs.renameSync(tmp, this.file); }
  account(accountId) { if (!accountId || typeof accountId !== 'string' || accountId.length > 80) throw new Error('invalid accountId'); if (!this.state.accounts[accountId]) this.state.accounts[accountId] = { id: accountId, createdAt: new Date().toISOString() }; return this.state.accounts[accountId]; }
  createCrew(accountId) { this.account(accountId); const crew = { id: id('crew'), leaderId: accountId, members: [accountId], ready: {} }; this.state.crews[crew.id] = crew; this.save(); return crew; }
  joinCrew(crewId, accountId) { this.account(accountId); const crew = this.state.crews[crewId]; if (!crew) throw new Error('crew not found'); if (!crew.members.includes(accountId) && crew.members.length >= this.config.lobby.maxCrewSize) throw new Error('crew is full'); if (!crew.members.includes(accountId)) crew.members.push(accountId); this.save(); return crew; }
  reserve(crewId, region) { const crew = this.state.crews[crewId]; if (!crew) throw new Error('crew not found'); const active = Object.values(this.state.reservations).filter(r => r.status === 'active' && r.region === region); const used = active.reduce((n, r) => n + r.playerCount, 0); if (used + crew.members.length > this.config.lobby.maxPlayers) throw new Error('lobby capacity reached'); const reservation = { id: id('res'), crewId, region, playerCount: crew.members.length, status: 'active', expiresAt: new Date(Date.now() + 5 * 60_000).toISOString() }; this.state.reservations[reservation.id] = reservation; this.save(); return reservation; }
  bindSession(reservationId, accountId) { const r = this.state.reservations[reservationId]; if (!r || r.status !== 'active') throw new Error('reservation unavailable'); const crew = this.state.crews[r.crewId]; if (!crew.members.includes(accountId)) throw new Error('account is not in crew'); const token = crypto.randomBytes(32).toString('base64url'); const session = { id: id('ses'), reservationId, accountId, token, expiresAt: new Date(Date.now() + 15 * 60_000).toISOString() }; this.state.sessions[session.id] = session; this.save(); return session; }
  authenticate(token) { const session = Object.values(this.state.sessions).find(s => s.token === token && Date.parse(s.expiresAt) > Date.now()); if (!session) throw new Error('invalid or expired session'); return session; }
  spawnStarterVehicle(crewId, accountId) { const crew = this.state.crews[crewId]; if (!crew || crew.leaderId !== accountId) throw new Error('only the crew leader may spawn the vehicle'); const existing = Object.values(this.state.vehicles).find(v => v.crewId === crewId && v.status === 'stored'); if (existing) return existing; const vehicle = { id: id('veh'), assetId: this.config.world.vehicle.starterId, crewId, seats: this.config.world.vehicle.seats, occupants: [], condition: this.config.world.vehicle.conditionMax, destination: 'crew_garage', status: 'stored' }; this.state.vehicles[vehicle.id] = vehicle; this.save(); return vehicle; }
  boardVehicle(vehicleId, accountId) { const v = this.state.vehicles[vehicleId]; if (!v) throw new Error('vehicle not found'); const crew = this.state.crews[v.crewId]; if (!crew.members.includes(accountId)) throw new Error('account is not in crew'); if (v.occupants.includes(accountId)) return v; if (v.occupants.length >= v.seats) throw new Error('vehicle is full'); v.occupants.push(accountId); v.status = 'active'; this.save(); return v; }
  updateWorldPosition(accountId, destination) { const valid = this.config.world.destinations.some(d => d.id === destination && d.playable); if (!valid) throw new Error('destination is not playable'); const a = this.account(accountId); a.lastSafeDestination = destination; this.save(); return { accountId, destination }; }
  reconnectPosition(accountId) { const a = this.account(accountId); const valid = this.config.world.destinations.some(d => d.id === a.lastSafeDestination && d.playable); return valid ? a.lastSafeDestination : this.config.world.safeRecovery; }
}
module.exports = { Store };
