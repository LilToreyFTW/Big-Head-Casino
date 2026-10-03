# Open-world vertical slice

The first connected district is represented by versioned destinations in `backend/config/gameplay.json`: protected Arrival Plaza, Casino Strip, Grand Casino, Equipment Shop, Crew Garage, Service District, and Rooftop Overlook. Each destination is explicitly marked playable so the browser map and reconnect logic cannot advertise unfinished scenery.

The backend now supports a four-seat starter crew vehicle (`BHC_VEH_CREW_VAN`), leader-authorized garage spawn, crew-only boarding, bounded seat capacity, persisted vehicle condition, and validated reconnect destinations with Arrival Plaza as safe recovery.

The Unreal module adds `ABHCVehiclePawn`, a replicated four-seat authority hook. It is a gameplay integration point for the production vehicle asset and movement component; physics, collision damage, garage UI, and Pixel Streaming input binding remain next milestones. The current project has no authored city map or imported vehicle asset, so the district is not yet complete or art-final.
