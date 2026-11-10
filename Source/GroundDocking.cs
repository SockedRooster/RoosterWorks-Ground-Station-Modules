using System;
using UnityEngine;

// Keep the stock ModuleDockingNode state machines and save format. This
// ground-only policy locks crossfeed on and removes staging controls, including
// restored action bindings and controls rebuilt when reopening the part menu.
public sealed class ModuleRWGroundDocking : PartModule
{
    public override void OnLoad(ConfigNode node) { base.OnLoad(node); Enforce(); }
    public override void OnStart(StartState state) { base.OnStart(state); Enforce(); }
    public override void OnStartFinished(StartState state) { base.OnStartFinished(state); Enforce(); }
    public void LateUpdate()
    { if (HighLogic.LoadedSceneIsFlight || HighLogic.LoadedSceneIsEditor) Enforce(); }
    public void FixedUpdate() { if (HighLogic.LoadedSceneIsFlight) Enforce(); }
    private static bool ReferenceControl(string name)
    { return name == "MakeReferenceToggle" || name == "MakeReference" || name == "MakeReferenceTransform"; }
    private static bool LockedControl(string name)
    {
        string key = name.ToLowerInvariant();
        return key.Contains("xfeed") || key.Contains("crossfeed") || key == "togglestaging";
    }
    private static void HideEvents(BaseEventList events, bool hideReference = false, bool hideNaming = false)
    {
        foreach (BaseEvent control in events)
            if (LockedControl(control.name) || (hideReference && ReferenceControl(control.name)) ||
                (hideNaming && control.name.IndexOf("rename", StringComparison.OrdinalIgnoreCase) >= 0))
            {
                control.active = false; control.guiActive = false;
                control.guiActiveEditor = false; control.guiActiveUnfocused = false;
            }
    }
    private static void HideActions(BaseActionList actions, bool hideReference = false, bool hideNaming = false)
    {
        foreach (BaseAction control in actions)
            if (LockedControl(control.name) || (hideReference && ReferenceControl(control.name)) ||
                (hideNaming && control.name.IndexOf("rename", StringComparison.OrdinalIgnoreCase) >= 0))
            { control.active = false; control.actionGroup = KSPActionGroup.None; }
    }
    private static bool HiddenField(string name)
    {
        string key = name.ToLowerInvariant();
        return key == "crossfeed" || key == "stagingenabled" || key.Contains("portname") ||
            key.Contains("acquire") || key.Contains("capture") || key.Contains("dockingforce") || key == "undockejectionforce";
    }
    private string ConnectedTitle(ModuleDockingNode port)
    {
        Part connected = port.otherNode != null ? port.otherNode.part : null;
        if (connected == null)
        {
            AttachNode node = String.IsNullOrEmpty(port.referenceAttachNode) ? null : part.FindAttachNode(port.referenceAttachNode);
            if (node != null) connected = node.attachedPart;
        }
        if (connected == null && port.dockedPartUId != 0 && part.vessel != null)
            foreach (Part candidate in part.vessel.parts)
                if (candidate != part && candidate.flightID == port.dockedPartUId) { connected = candidate; break; }
        return connected != null && connected.partInfo != null && !String.IsNullOrEmpty(connected.partInfo.title)
            ? connected.partInfo.title : "Unconnected port";
    }
    private void Enforce()
    {
        if (part == null) return;
        part.fuelCrossFeed = true; part.stagingOn = false;
        string id = part.partInfo == null || String.IsNullOrEmpty(part.partInfo.name) ? "" : part.partInfo.name.Replace('_', '.');
        bool command = id == "RW.GND.CMD";
        bool hidePartReference = id.Length > 0 && !command;
        HideEvents(part.Events, hidePartReference); HideActions(part.Actions, hidePartReference);
        foreach (ModuleDockingNode port in part.FindModulesImplementing<ModuleDockingNode>())
        {
            if (!port.crossfeed) port.EnableXFeed();
            port.crossfeed = true;
            port.stagingEnabled = false;
            port.stagingToggleEnabledEditor = false;
            port.stagingToggleEnabledFlight = false;
            // Let stock magnetic torque straighten a broad initial approach.
            // Keep final capture close and aligned rather than locking crooked.
            // Separation beyond the acquire radius prevents immediate recapture.
            if (id.StartsWith("RW.GND.", StringComparison.Ordinal))
            {
                port.acquireRange = 2.5f; port.acquireForce = 40f;
                port.acquireTorque = 30f; port.acquireForceTweak = 100f;
                port.acquireMinFwdDot = .258819f; // cos(75 degrees)
                port.captureRange = .08f; port.captureMinFwdDot = .998f;
                port.captureMaxRvel = .3f; port.minDistanceToReEngage = 3f;
            }
            HideEvents(port.Events, true); HideActions(port.Actions, true);
            foreach (BaseField field in port.Fields)
                if (HiddenField(field.name))
                { field.guiActive = false; field.guiActiveEditor = false; }
            // Separate manual controls for each stock docking node. Staging
            // remains unavailable, while normal undocking/decoupling is kept.
            string label = ConnectedTitle(port);
            foreach (BaseEvent control in port.Events)
                if (control.name == "Undock" || control.name == "Decouple" || control.name == "UndockSameVessel")
                    control.guiName = "Undock(" + label + ")";
        }
        // Hide the optional NavyFish naming UI without a plugin dependency or
        // removing its persistent names/targeting support. Keep one command
        // module reference control on CMD; never expose port reference controls.
        foreach (PartModule module in part.Modules)
        {
            bool naming = module.GetType().Name == "ModuleDockingNodeNamed";
            bool reference = module is ModuleDockingNode || (id.Length > 0 && (!command || !(module is ModuleCommand)));
            HideEvents(module.Events, reference, naming); HideActions(module.Actions, reference, naming);
            if (module is ModuleDockingNode || naming)
                foreach (BaseField field in module.Fields)
                    if (HiddenField(field.name)) { field.guiActive = false; field.guiActiveEditor = false; }
        }
        // EnableXFeed may rebuild part actions; reassert part-wide restrictions
        // last as well as on every menu/physics refresh.
        part.fuelCrossFeed = true; part.stagingOn = false;
        HideEvents(part.Events, hidePartReference); HideActions(part.Actions, hidePartReference);
    }
    public override string GetInfo()
    { return "Integrated docking with strong pull and wide-angle alignment assistance within 2.5 m on ground ports. Crossfeed is always enabled; no staging. Release controls identify the connected part. Ground CMD retains the command reference control."; }
}
