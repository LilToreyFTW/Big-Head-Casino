#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "BHCGameMode.generated.h"

UCLASS()
class ABHCGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ABHCGameMode();
    virtual void StartPlay() override;
    virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;
    virtual void PostLogin(APlayerController* NewPlayer) override;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Lobby") int32 MaxPlayers = 100;
private:
    void EnsurePlayablePawn();
};
