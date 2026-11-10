using UnityEngine;
using System.Collections.Generic;

// Follow the greenhouse's existing inspection-light switch without coupling
// the end windows to its independent grow lamps or changing either control.
public sealed class ModuleRWEndWindowLink : PartModule
{
    [KSPField] public string sourceLightName = "RW_GreenhouseInspectionLight";
    private ModuleLight source;
    private List<Renderer> renderers;
    private MaterialPropertyBlock block;
    public override void OnStart(StartState state)
    {
        base.OnStart(state);
        if (part == null) return;
        renderers = part.FindModelComponents<Renderer>("RW_EndWindows");
        block = new MaterialPropertyBlock();
        foreach (ModuleLight light in part.FindModulesImplementing<ModuleLight>())
            if (light.lightName == sourceLightName) { source = light; break; }
        LateUpdate();
    }
    public void LateUpdate()
    {
        if (source == null || renderers == null || block == null) return;
        Color color = source.isOn ? new Color(.93f, .84f, .67f, 1f) : new Color(0, 0, 0, 1f);
        foreach (Renderer renderer in renderers)
        {
            if (renderer == null) continue;
            renderer.GetPropertyBlock(block); block.SetColor("_EmissiveColor", color); renderer.SetPropertyBlock(block);
        }
    }
}
