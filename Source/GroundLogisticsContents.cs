using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

// Independent editor payload selector. No flight reconciliation: old vessels,
// depleted resources and Kerbalism background state are never refilled/migrated.
public sealed class ModuleRWGroundLogisticsContents : PartModule
{
    [KSPField] public string profileSet = "RW_GND_LOG";
    [KSPField(isPersistant = true, guiActiveEditor = true, guiName = "Logistics contents")]
    [UI_ChooseOption(options = new[] { "Mixed supplies", "Food", "Water", "Oxygen", "Nitrogen", "Ammonia", "Carbon Dioxide", "Hydrogen", "Waste", "WasteWater" }, affectSymCounterparts = UI_Scene.Editor)]
    public string contents = "Mixed supplies";
    private static readonly string[] managed = { "Food", "Water", "Oxygen", "Nitrogen", "Ammonia", "CarbonDioxide", "Hydrogen", "Waste", "WasteWater" };
    private string applied;
    private int scan;
    public override void OnStart(StartState state)
    {
        base.OnStart(state);
        var control = Fields["contents"].uiControlEditor;
        if (control != null) { control.onFieldChanged += Changed; control.onSymmetryFieldChanged += Changed; }
        if (HighLogic.LoadedSceneIsEditor) Apply();
    }
    private void Changed(BaseField field, object previous) { if (HighLogic.LoadedSceneIsEditor) Apply(); }
    public void Update() { if (HighLogic.LoadedSceneIsEditor && (contents != applied || ++scan % 30 == 0)) Apply(); }
    private ConfigNode Choice()
    {
        if (GameDatabase.Instance == null) return null;
        foreach (ConfigNode set in GameDatabase.Instance.GetConfigNodes("RW_LOG_LOADOUTS"))
        {
            if (set.GetValue("name") != profileSet) continue;
            foreach (ConfigNode choice in set.GetNodes("LOADOUT"))
                if (choice.GetValue("name") == contents) return choice;
        }
        return null;
    }
    private void Apply()
    {
        if (part == null || PartResourceLibrary.Instance == null) return;
        ConfigNode choice = Choice();
        if (choice == null) return;
        var selected = new Dictionary<string, ConfigNode>();
        foreach (ConfigNode spec in choice.GetNodes("RESOURCE"))
        {
            string name = spec.GetValue("name");
            // Atomic availability check before removing any existing cargo.
            if (PartResourceLibrary.Instance.GetDefinition(name) == null) return;
            selected.Add(name, spec);
        }
        bool selectionChanged = applied != null && contents != applied;
        bool changed = false;
        foreach (string name in managed)
        {
            if (!selected.ContainsKey(name))
            {
                if (part.Resources[name] != null) { part.Resources.Remove(name); changed = true; }
                continue;
            }
            ConfigNode spec = selected[name];
            double maximum = double.Parse(spec.GetValue("maxAmount"), CultureInfo.InvariantCulture);
            PartResource resource = part.Resources[name];
            if (resource == null) { part.AddResource(spec); changed = true; }
            else if (Math.Abs(resource.maxAmount - maximum) > 1e-7)
            {
                double fraction = resource.maxAmount > 0 ? resource.amount / resource.maxAmount : 0;
                resource.maxAmount = maximum;
                resource.amount = Math.Max(0, Math.Min(maximum, fraction * maximum));
                changed = true;
            }
        }
        applied = contents;
        if (!changed) return;
        GameEvents.onPartResourceListChange.Fire(part);
        MonoUtilities.RefreshContextWindows(part);
        // Repairs don't fire ship-modified again, avoiding listener reset loops.
        if (selectionChanged && EditorLogic.fetch != null && EditorLogic.fetch.ship != null)
            GameEvents.onEditorShipModified.Fire(EditorLogic.fetch.ship);
    }
    public override string GetInfo() { return "Choose mixed supplies or dedicated Food, Water, Oxygen, Nitrogen, Ammonia, Carbon Dioxide, Hydrogen, Waste or WasteWater storage in the editor. Waste tanks start empty. Mixed loadout reserves 60% of capacity for food, water and oxygen. Dedicated capacities are calibrated by resource;; stock item inventory remains separate."; }
}
