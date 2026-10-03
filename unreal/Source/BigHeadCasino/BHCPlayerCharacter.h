#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "BHCPlayerCharacter.generated.h"

UCLASS()
class ABHCPlayerCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ABHCPlayerCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
protected:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void Turn(float Value);
    void LookUp(float Value);
    void StartSprint();
    void StopSprint();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera") class USpringArmComponent* CameraBoom;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera") class UCameraComponent* FollowCamera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual") class UStaticMeshComponent* BodyMesh;
    UPROPERTY(EditDefaultsOnly, Category="Movement") float WalkSpeed = 420.0f;
    UPROPERTY(EditDefaultsOnly, Category="Movement") float SprintSpeed = 700.0f;
};
