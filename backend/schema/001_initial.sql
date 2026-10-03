-- Reference schema for the production transactional store. The Phase 1 local
-- service uses the same entities in JSON so it can run without dependencies.
CREATE TABLE accounts (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, self_excluded_until TEXT);
CREATE TABLE crews (id TEXT PRIMARY KEY, leader_id TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE crew_members (crew_id TEXT NOT NULL, account_id TEXT NOT NULL, ready INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (crew_id, account_id));
CREATE TABLE lobbies (id TEXT PRIMARY KEY, region TEXT NOT NULL, max_players INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE reservations (id TEXT PRIMARY KEY, lobby_id TEXT NOT NULL, crew_id TEXT NOT NULL, player_count INTEGER NOT NULL, status TEXT NOT NULL, expires_at TEXT NOT NULL);
CREATE TABLE sessions (id TEXT PRIMARY KEY, reservation_id TEXT NOT NULL, account_id TEXT NOT NULL, token_hash TEXT NOT NULL, expires_at TEXT NOT NULL, revoked_at TEXT);
CREATE TABLE audit_events (id TEXT PRIMARY KEY, actor_id TEXT, event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
