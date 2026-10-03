#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "BHCVehiclePawn.generated.h"

UCLASS()
class ABHCVehiclePawn : public APawn
{
    GENERATED_BODY()
public:
    ABHCVehiclePawn();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    UFUNCTION(Server, Reliable) void ServerEnterVehicle(APlayerController* RequestingPlayer);
    UFUNCTION(Server, Reliable) void ServerExitVehicle(APlayerController* RequestingPlayer);
    UPROPERTY(Replicated, BlueprintReadOnly, Category="Vehicle") TArray<APlayerController*> Occupants;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Vehicle") int32 SeatCount = 4;
    UPROPERTY(Replicated, BlueprintReadOnly, Category="Vehicle") float Condition = 100.0f;
protected:
    virtual void BeginPlay() override;
};
