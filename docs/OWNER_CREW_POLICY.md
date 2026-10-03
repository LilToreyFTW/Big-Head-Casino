# Owner crew policy

`crew_4e5c775890ba` is reserved for the account `Big Head Developer`. The crew is invite-only, and its members are marked `combatImmune` in authoritative session data. Creating the owner account again returns the same crew instead of creating a duplicate. Joining requires the invite token returned by the leader-only invite endpoint.

This protects the owner crew in the current backend/browser slice. The Unreal combat-authority layer must consume the same owner-crew flag before public combat is enabled.
