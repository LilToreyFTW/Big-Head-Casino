#include "BHCVehiclePawn.h"
#include "Net/UnrealNetwork.h"
#include "GameFramework/PlayerController.h"

ABHCVehiclePawn::ABHCVehiclePawn() { bReplicates = true; SetReplicateMovement(true); PrimaryActorTick.bCanEverTick = false; }
void ABHCVehiclePawn::BeginPlay() { Super::BeginPlay(); }
void ABHCVehiclePawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const { Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ABHCVehiclePawn, Occupants); DOREPLIFETIME(ABHCVehiclePawn, Condition); }
void ABHCVehiclePawn::ServerEnterVehicle_Implementation(APlayerController* RequestingPlayer) { if (!RequestingPlayer || Occupants.Contains(RequestingPlayer) || Occupants.Num() >= SeatCount) return; Occupants.Add(RequestingPlayer); }
void ABHCVehiclePawn::ServerExitVehicle_Implementation(APlayerController* RequestingPlayer) { if (HasAuthority()) Occupants.Remove(RequestingPlayer); }
