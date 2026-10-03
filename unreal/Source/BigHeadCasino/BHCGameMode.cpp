#include "BHCGameMode.h"
#include "BHCPlayerCharacter.h"
#include "GameFramework/PlayerController.h"
ABHCGameMode::ABHCGameMode() { bUseSeamlessTravel = true; DefaultPawnClass = ABHCPlayerCharacter::StaticClass(); }
void ABHCGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);
    // Phase 1 hook: authenticated reservation binding belongs here once the
    // Pixel Streaming session identity is available to the UE process.
}
