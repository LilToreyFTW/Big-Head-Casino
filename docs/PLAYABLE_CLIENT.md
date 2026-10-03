# Playable client status

The browser URL currently serves the crew/session shell. It cannot spawn an Unreal character by itself because the project does not yet have a running Pixel Streaming signalling server and GPU-backed Unreal client allocation.

The Unreal project now has a real replicated third-person pawn, `ABHCPlayerCharacter`, with a spring-arm camera and WASD, mouse-look, jump, and sprint input. `ABHCGameMode` selects it as the default pawn. The C++ target builds successfully with Unreal Engine 5.7.

To play the current Unreal slice locally, open `unreal/BigHeadCasino.uproject` in UE 5.7, press Play, and use WASD, mouse, Space, and Left Shift. Browser play requires the next infrastructure step: package the client, run Pixel Streaming 2 signalling and frontend services, allocate one client process per authenticated player, and bind the browser session to its pawn.

This distinction is deliberate: the Vercel page is not presented as native browser Unreal execution, and the current shell does not claim that a streamed client is connected.
