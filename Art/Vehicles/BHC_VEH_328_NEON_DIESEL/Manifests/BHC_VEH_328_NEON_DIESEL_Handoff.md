# BHC_VEH_328_NEON_DIESEL handoff

Mandatory instruction: **"create it fully 3D and very high end no BS."**

The Blender vehicle is a complete inferred game asset built from the approved four-angle board: graphite widebody shell, riveted flares, vented hood, carbon aero, twin grille, cool-white lights, 328 intercooler, deep-dish wheels, warm brake calipers, giant rear wing, four round exhausts, exact two-line red door branding on both sides, modeled cabin for one driver plus three passengers, independent doors/hood/trunk, engine bay with fictional turbo presentation, rig bones, locators, collision proxies, and LOD guidance meshes.

## Export contract

Forward +X, up +Z, lateral +Y, meters, import scale 1.0. Existing `ABHCVehiclePawn` exposes `SeatCount = 4`; the source rig contains `Chassis`, four wheels, four doors, `Hood`, `Trunk`, and `SteeringWheel`. Standard visual setup is RWD; the same mesh supports Sol's optional AWD handling.

## Actual files

- `Blender/BHC_VEH_328_NEON_DIESEL_Master.blend`
- `Exports/BHC_VEH_328_NEON_DIESEL.glb`
- `Exports/BHC_VEH_328_NEON_DIESEL.fbx`
- `Collision/COL_BHC_328_*.fbx`
- `Manifests/BHC_VEH_328_NEON_DIESEL_manifest.json`
- `Previews/BHC_VEH_328_NEON_DIESEL_FourAngle.png` and detail renders

## Sol owns the remaining stage

Unreal driving physics, entry/exit, multiplayer synchronization, seat ownership, lights/effects, RWD/AWD torque behavior, garage persistence, recovery, neutral-player protection, and actual performance/acceptance testing remain Sol integration responsibilities. This report does not claim the vehicle has been driven or network-tested in Unreal.
