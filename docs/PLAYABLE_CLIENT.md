# Playable client status

The browser URL serves the crew/session shell. It does not launch Unreal by itself. The actual browser playable client is the local Pixel Streaming 2 player at `http://127.0.0.1/`, backed by a running UE 5.7 process.

The Unreal project now has a real replicated third-person pawn, `ABHCPlayerCharacter`, with a spring-arm camera and WASD, mouse-look, jump, and sprint input. `ABHCGameMode` selects it as the default pawn. The C++ target builds successfully with Unreal Engine 5.7.

To play locally in the editor, open `unreal/BigHeadCasino.uproject` in UE 5.7, press Play, and use WASD, mouse, Space, and Left Shift. To stream the game into a browser, run the UE 5.7 Pixel Streaming 2 `SignallingWebServer` on ports 80/8888, then launch:

```text
UnrealEditor.exe unreal/BigHeadCasino.uproject -game -dx11 -sm5 -PixelStreamingURL=ws://127.0.0.1:8888 -RenderOffScreen -AllowSoftwareRendering -Unattended -NoSplash
```

Open `http://127.0.0.1/`, click the video to start input, then use WASD, mouse, Space, and Left Shift. The runtime game mode spawns a third-person pawn and a lit greybox district so the first streamed frame is playable even before the authored city map is finished.

The public Vercel page remains the crew/session shell because Vercel does not host the GPU-backed Unreal process. A public Unreal stream needs a separate Pixel Streaming host and signalling endpoint.
