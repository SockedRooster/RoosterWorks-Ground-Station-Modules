// A plain ModuleDecouple releases this entire part: no anchored baseplate.
public sealed class ModuleRWPodRelease : PartModule
{
    private ModuleDecouple release;
    public override void OnStart(StartState state) { base.OnStart(state); Bind(); }
    public override void OnStartFinished(StartState state) { base.OnStartFinished(state); Bind(); }
    private void Bind()
    {
        if (part == null) return;
        release = part.FindModuleImplementing<ModuleDecouple>();
        if (release == null) return;
        if (release.Events.Contains("Decouple")) { release.Events["Decouple"].guiActive = false; release.Events["Decouple"].guiActiveEditor = false; }
        if (Events.Contains("ReleasePod")) Events["ReleasePod"].active = !release.isDecoupled;
        foreach (BaseAction action in release.Actions) action.active = false;
    }
    [KSPEvent(guiActive = true, guiActiveEditor = false, guiName = "Decouple Thrust Pod")]
    public void ReleasePod()
    {
        if (!HighLogic.LoadedSceneIsFlight || part == null) return;
        if (release == null) Bind();
        if (release == null || release.isDecoupled) return;
        foreach (ModuleEngines engine in part.FindModulesImplementing<ModuleEngines>()) engine.Shutdown();
        release.Decouple();
        if (Events.Contains("ReleasePod")) Events["ReleasePod"].active = !release.isDecoupled;
    }
    [KSPAction("Decouple Thrust Pod")] public void ReleaseAction(KSPActionParam p) { ReleasePod(); }
}
