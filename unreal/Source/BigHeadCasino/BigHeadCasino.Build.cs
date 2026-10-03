using UnrealBuildTool;
public class BigHeadCasino : ModuleRules
{
    public BigHeadCasino(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "NetCore" });
    }
}
