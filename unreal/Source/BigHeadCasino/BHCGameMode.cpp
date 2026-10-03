#include "BHCGameMode.h"
#include "BHCPlayerCharacter.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/PlayerController.h"
#include "UObject/ConstructorHelpers.h"
ABHCGameMode::ABHCGameMode() { bUseSeamlessTravel = true; DefaultPawnClass = ABHCPlayerCharacter::StaticClass(); }
void ABHCGameMode::StartPlay()
{
    Super::StartPlay();
    UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (!Cube || !GetWorld()) return;
    auto SpawnBlock = [this, Cube](const FVector& Location, const FVector& Scale, const TCHAR* Name)
    {
        FActorSpawnParameters Params;
        Params.Name = FName(Name);
        AStaticMeshActor* Block = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Location, FRotator::ZeroRotator, Params);
        if (Block) { Block->GetStaticMeshComponent()->SetStaticMesh(Cube); Block->SetActorScale3D(Scale); }
    };
    // A deterministic greybox district keeps the project playable even before
    // the authored city map and streamed assets are available.
    SpawnBlock(FVector(0, 0, -50), FVector(30, 30, 0.5f), TEXT("BHC_GreyboxFloor"));
    SpawnBlock(FVector(0, 900, 350), FVector(8, 2, 4), TEXT("BHC_CasinoBlock"));
    SpawnBlock(FVector(900, 0, 250), FVector(2, 8, 3), TEXT("BHC_HotelBlock"));
    SpawnBlock(FVector(-900, 0, 200), FVector(2, 6, 2.5f), TEXT("BHC_GarageBlock"));
}
AActor* ABHCGameMode::ChoosePlayerStart_Implementation(AController* Player)
{
    for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It) return *It;
    if (!GetWorld()) return nullptr;
    return GetWorld()->SpawnActor<APlayerStart>(APlayerStart::StaticClass(), FVector(0, 0, 180), FRotator::ZeroRotator);
}
void ABHCGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);
    // Phase 1 hook: authenticated reservation binding belongs here once the
    // Pixel Streaming session identity is available to the UE process.
}
