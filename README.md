# Big Head Casino

Phase 1 isolated project package for the Big Head Casino multiplayer game.

## Current status

Implemented and locally verified:

- Node.js session/crew backend with durable JSON persistence.
- Four-player crew reservations and a 100-player lobby capacity gate.
- Open-world destination registry, crew vehicle seat authority, garage spawn, and safe reconnect positions.
- Short-lived authenticated browser session tokens bound to a player.
- Static browser landing page for sign-in, crew creation/join, region selection, and reservation.
- Versioned gameplay configuration and database schema.
- Automated backend tests.

Implemented and verified:

- Unreal Engine 5.7 project generation and `BigHeadCasinoEditor` C++ build using the installed Visual Studio 2022 toolchain.
- Headless Unreal game startup, `/Engine/Maps/Entry` load, `BHCGameMode` selection, and clean engine shutdown.
- Replicated Unreal four-seat vehicle authority hook (`ABHCVehiclePawn`).

Implemented but unverified:

- Pixel Streaming 2 integration points and independent browser-controlled streams.
- Authored connected city map, vehicle physics/animation, and production interiors are still pending asset/world integration.

Blocked on this host:

- Pixel Streaming 2 infrastructure and GPU capacity are not available for independent-stream testing.

## Run the verified increment

Requires Node.js 20 or newer. From this directory:

```powershell
node backend/server.js
```

Open <http://localhost:8080>. The service stores state in `backend/data/state.json`; set `BHC_DATA_FILE` to use another path.

Run tests:

```powershell
node --test backend/test/*.test.js
```

## Unreal setup

Open `unreal/BigHeadCasino.uproject` with Unreal Engine 5.7. `unreal/ENGINE_VERSION.md` records the verified engine location and Pixel Streaming compatibility follow-up.

## Security boundaries

The backend owns player identity, crew membership, lobby capacity, reservation, and session binding. Clients submit intents; they do not choose outcomes or another player's session. This Phase 1 service is a development skeleton and has no production account provider, TLS termination, payment integration, or casino outcome implementation.
