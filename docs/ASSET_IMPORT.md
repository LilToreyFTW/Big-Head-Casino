# Asset import contract

`Art/Manifests/BHC_First_Batch_manifest.json` is the source of truth for the first Astra batch. Import source files from `Art/Exports` into `/Game/BHC/Art/<AssetID>` with GLB/FBX scale `1.0`; preserve the source `.blend` separately. The manifest's one-meter reference cube must measure one Unreal meter before bulk import. Keep the stable `BHC_` asset ID in the Unreal asset name and user data.

The current batch contains the modular environment, big-head player mesh, AK47, and blackjack prop. The remaining roster IDs from the brief are not present in this batch and remain an integration dependency.
