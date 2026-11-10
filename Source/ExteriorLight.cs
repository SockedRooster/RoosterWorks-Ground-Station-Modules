using System.Collections.Generic;
using UnityEngine;

// Explicit real lights; emission alone does not illuminate terrain.
public sealed class ModuleRWExteriorLight : PartModule
{
    [KSPField] public string lightName = "RW_DoorSpot";
    [KSPField] public string lightMeshRendererName = "RW_DoorLightLens";
    [KSPField] public float resourceAmount = .03f;
    [KSPField(isPersistant = true)] public bool isOn;
    [KSPField(isPersistant = true)] public bool followCabinLights = true;
    [KSPField(guiActive = true, guiActiveEditor = true, guiName = "Exterior light")]
    public string status = "Following cabin lights";
    private List<Light> lamps;
    private List<Renderer> lenses;
    private ModuleColorChanger cabin;
    private MaterialPropertyBlock block;
    private bool powered;
    public override void OnStart(StartState state)
    { base.OnStart(state); Bind(); Group(); UpdateRequest(); Apply(); }
    public override void OnStartFinished(StartState state)
    { base.OnStartFinished(state); Bind(); Group(); UpdateRequest(); Apply(); }
    private void Bind()
    {
        if (part == null) return;
        lamps = part.FindModelComponents<Light>(lightName);
        if (lamps.Count == 0)
        {
            Transform mount = part.FindModelTransform(lightName);
            if (mount != null)
            {
                Light lamp = mount.gameObject.GetComponent<Light>();
                if (lamp == null) lamp = mount.gameObject.AddComponent<Light>();
                lamps.Add(lamp);
            }
        }
        lenses = part.FindModelComponents<Renderer>(lightMeshRendererName);
        if (block == null) block = new MaterialPropertyBlock();
        cabin = null;
        foreach (ModuleColorChanger source in part.FindModulesImplementing<ModuleColorChanger>())
            if ((source.moduleID ?? "").Contains("CabinLights")) { cabin = source; break; }
        foreach (Light lamp in lamps)
        {
            if (lamp == null) continue;
            lamp.type = LightType.Spot; lamp.renderMode = LightRenderMode.ForcePixel;
            lamp.range = 10f; lamp.spotAngle = 100f; lamp.intensity = 4f;
            lamp.color = new Color(1f, .91f, .76f, 1f); lamp.cullingMask = -1;
            lamp.shadows = LightShadows.None;
            lamp.transform.localRotation = Quaternion.Euler(60f, 0f, 0f);
        }
    }
    private void Group()
    {
        var group = new BasePAWGroup("RWLighting", "Lighting", true);
        foreach (BaseEvent e in Events) e.group = group;
        foreach (BaseField f in Fields) f.group = group;
    }
    private void UpdateRequest()
    {
        if (followCabinLights && cabin != null) isOn = cabin.animState;
        if (HighLogic.LoadedSceneIsEditor) powered = isOn;
        if (HighLogic.LoadedSceneIsFlight && (vessel == null || !vessel.loaded || vessel.packed)) powered = false;
        if (!isOn) powered = false;
    }
    [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Exterior Light On")]
    public void LightsOn() { followCabinLights = false; isOn = true; UpdateRequest(); Apply(); }
    [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Exterior Light Off")]
    public void LightsOff() { followCabinLights = false; isOn = false; powered = false; Apply(); }
    [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Link Exterior to Cabin Lights")]
    public void LinkToCabin() { followCabinLights = true; UpdateRequest(); Apply(); }
    [KSPAction("Toggle Exterior Light", KSPActionGroup.Light)]
    public void ToggleLightAction(KSPActionParam p) { if (isOn) LightsOff(); else LightsOn(); }
    [KSPAction("Exterior Light On")] public void LightOnAction(KSPActionParam p) { LightsOn(); }
    [KSPAction("Exterior Light Off")] public void LightOffAction(KSPActionParam p) { LightsOff(); }
    public void LateUpdate()
    {
        if (part == null) return;
        if (lamps == null || lamps.Count == 0) Bind();
        UpdateRequest(); Apply();
    }
    public void FixedUpdate()
    {
        if (!HighLogic.LoadedSceneIsFlight || part == null) return;
        UpdateRequest(); powered = false;
        if (isOn && vessel != null && vessel.loaded && !vessel.packed)
        {
            double required = resourceAmount * Time.fixedDeltaTime;
            powered = required <= 0 || part.RequestResource("ElectricCharge", required) >= required * .999;
        }
        Apply();
    }
    private void Apply()
    {
        bool on = isOn && powered;
        if (lamps != null) foreach (Light lamp in lamps) if (lamp != null) lamp.enabled = on;
        if (lenses != null && block != null) foreach (Renderer lens in lenses)
        {
            if (lens == null) continue;
            lens.GetPropertyBlock(block); block.SetColor("_EmissiveColor", on ? new Color(1f,.91f,.76f,1f) : new Color(0,0,0,1)); lens.SetPropertyBlock(block);
        }
        status = !isOn ? "Off" : on ? "Illuminating stairs / ground" : "Waiting for electric charge";
        if (followCabinLights) status += " (linked to cabin)";
    }
    public override string GetInfo() { return "Warm-white real spotlight over door; 10 m range; 0.03 EC/s. Follows cabin lights until manually overridden."; }
}
