# Big Head Casino — First Complete Asset Batch

Mandatory project instruction: **"create it fully 3D and very high end no BS."**

## Created in Blender

- `BHC_ENV_MODULAR_KIT`: connected premium room slice with modular floor, walls, columns, trims, entrance portal and original logo, balcony/railing, stair steps, service counter cover, staff door/keycard housing, warning light, security camera, smoked-glass partitions, chandelier and one-meter reference cube.
- `BHC_SK_PLAYER_BIGHEAD`: oversized expressive adult bobble-head player with glasses, suit, shoes, gloves, standardized armature, head-wobble bone, attachment sockets, hit-volume guidance and named animation clip inventory.
- `BHC_WP_AK47`: original casino-presented AK-inspired hero weapon with world/first-person/third-person source variants, separate receiver/barrel/muzzle/stock/grip/magazine pieces, brass inlay, collision proxy, attachment markers and animation-event metadata.
- `BHC_PROP_BLACKJACK`: complete blackjack table prop with walnut base, brass and emerald felt layers, dealer rail, five player positions, seats, card markers, chip rings, shoe, discard tray and editable sign/card/chip pieces.

## Exported files

- `Art/Blender/BHC_First_Batch.blend` — editable source scene.
- `Art/Exports/BHC_ENV_MODULAR_KIT.glb`
- `Art/Exports/BHC_SK_PLAYER_BIGHEAD.glb`
- `Art/Exports/BHC_WP_AK47.glb`
- `Art/Exports/BHC_PROP_BLACKJACK.glb`
- Matching Unreal-friendly FBX exports are also present beside each GLB (`BHC_ENV_MODULAR_KIT.fbx`, `BHC_SK_PLAYER_BIGHEAD.fbx`, `BHC_WP_AK47.fbx`, `BHC_PROP_BLACKJACK.fbx`).
- `Art/Previews/BHC_Overview.png`
- `Art/Previews/BHC_Character.png`
- `Art/Previews/BHC_AK47.png`
- `Art/Previews/BHC_Blackjack.png`
- `Art/Manifests/BHC_First_Batch_manifest.json`

## Sol integration handoff

Sol can import the GLB files at scale 1.0 (one Blender unit equals one meter), retain the named `ATT_BHC_*` sockets and `COL_BHC_*` collision proxy, use the armature custom properties for hit-volume and head-wobble bounds, and attach gameplay/UI to the editable surfaces. The server remains authoritative for blackjack outcomes, weapon simulation, and all multiplayer state.

## Remaining work

The first batch is complete as a high-end editable art foundation. The remaining brief calls for production reduction and deformation QA, full animation authoring, the other six weapon families, all other casino game props, daily wheels, cases/skins/knives/gloves, supporting spaces, NPC variants, and final Unreal import validation. LOD1/LOD2 budgets are recorded as guidance metadata in this batch and should be authored as final reduced meshes during Sol's integration pass.
