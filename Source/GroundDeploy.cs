using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

// Ground-only procedural pose animation. The existing station plugins and
// source models remain untouched. Moving visuals and collision share parents.
public sealed class ModuleRWGroundDeploy : PartModule
{
    [KSPField] public string deploymentID = "Legs";
    [KSPField] public float duration = 2.5f;
    [KSPField(isPersistant = true)] public bool deployed = true;
    [KSPField(isPersistant = true)] public float deployment = 1f;
    [KSPField(isPersistant = true)] public bool evaLockOwned;
    [KSPField(isPersistant = true)] public bool evaRestrictionBeforeLock;
    [KSPField(isPersistant = true)] public string supportFit = "";
    [KSPField(guiActiveEditor = true, guiActive = true, guiName = "Deployment")]
    public string status = "Deployed";
    private readonly List<Binding> bindings = new List<Binding>();
    private ConfigNode[] specifications;
    private Collider hatch;
    private sealed class Binding
    {
        public Transform transform;
        public Vector3 startPosition, endPosition;
        public Quaternion startRotation, endRotation;
        public Collider[] colliders;
        public RWGroundFit fit;
        public float adjustment;
    }
    public override void OnLoad(ConfigNode node)
    {
        base.OnLoad(node);
        ConfigNode[] found = node.GetNodes("TRANSFORM");
        if (found.Length > 0) specifications = found;
    }
    public override void OnStart(StartState state)
    {
        base.OnStart(state);
        if (!(HighLogic.LoadedSceneIsEditor || HighLogic.LoadedSceneIsFlight)) return;
        if (HighLogic.LoadedSceneIsEditor && evaLockOwned)
        {
            part.noAutoEVAAny = evaRestrictionBeforeLock;
            evaLockOwned = false;
        }
        // Craft/save MODULE nodes contain persistent state, not geometry bindings.
        if (specifications == null && part.partInfo != null)
            foreach (ConfigNode node in part.partInfo.partConfig.GetNodes("MODULE"))
                if (node.GetValue("name") == "ModuleRWGroundDeploy" && node.GetValue("deploymentID") == deploymentID)
                    specifications = node.GetNodes("TRANSFORM");
        foreach(Binding old in bindings)if(old.fit!=null)old.fit.Dispose();
        bindings.Clear();
        if (deploymentID == "Stairs")
            foreach (Collider candidate in part.GetComponentsInChildren<Collider>(true))
                if (candidate.name == "Ground_EVA_Airlock" && candidate.isTrigger && candidate.CompareTag("Airlock")) hatch = candidate;
        if (specifications != null)
            foreach (ConfigNode node in specifications)
                foreach (Transform transform in part.FindModelTransforms(node.GetValue("name")))
                    bindings.Add(new Binding {
                        transform = transform, startPosition = Vector(node.GetValue("deployPosition")),
                        endPosition = Vector(node.GetValue("retractPosition")),
                        startRotation = Quaternion.identity,
                        endRotation = Quaternion.Euler(Vector(node.GetValue("retractEuler"))),
                        colliders = transform.GetComponentsInChildren<Collider>(true)
                    });
        if (bindings.Count == 0) Debug.LogError("[RoosterWorks Ground] No " + deploymentID + " motion bindings on " + part.name);
        string[] saved=(supportFit??"").Split(';');
        for(int i=0;i<bindings.Count;i++)
        {
            Binding b=bindings[i];b.fit=new RWGroundFit(b.transform,deploymentID=="Stairs");
            float value;
            if(i<saved.Length&&float.TryParse(saved[i],NumberStyles.Float,CultureInfo.InvariantCulture,out value)&&!float.IsNaN(value)&&!float.IsInfinity(value))
                b.adjustment=Mathf.Clamp(value,deploymentID=="Stairs"?-15f:-.65f,deploymentID=="Stairs"?15f:.35f);
        }
        deployment = Mathf.Clamp01(deployment);
        Fields["status"].guiName = deploymentID == "Legs" ? "Support legs" : "Access stairs";
        string lower = deploymentID == "Legs" ? "Lower Legs" : "Lower Stairs";
        string raise = deploymentID == "Legs" ? "Raise Legs" : "Raise Stairs";
        Events["Deploy"].guiName = lower; Events["Retract"].guiName = raise;
        Actions["DeployAction"].guiName = lower; Actions["RetractAction"].guiName = raise;
        Actions["ToggleAction"].guiName = deploymentID == "Legs" ? "Toggle Legs" : "Toggle Stairs";
        BaseAction gear = Actions["GearAction"];
        gear.active = gear.activeEditor = deploymentID == "Legs";
        if (deploymentID != "Legs") gear.actionGroup = KSPActionGroup.None;
        ApplyPose();
    }
    private static Vector3 Vector(string value)
    {
        string[] items = value.Split(',');
        return new Vector3(float.Parse(items[0], CultureInfo.InvariantCulture),
            float.Parse(items[1], CultureInfo.InvariantCulture), float.Parse(items[2], CultureInfo.InvariantCulture));
    }
    [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Lower")]
    public void Deploy() { SetTarget(true, true); }
    [KSPEvent(guiActive = true, guiActiveEditor = true, guiName = "Raise")]
    public void Retract() { SetTarget(false, true); }
    [KSPAction("Lower")] public void DeployAction(KSPActionParam action) { Deploy(); }
    [KSPAction("Raise")] public void RetractAction(KSPActionParam action) { Retract(); }
    [KSPAction("Toggle")] public void ToggleAction(KSPActionParam action)
    {
        if (action.group == KSPActionGroup.Gear && deploymentID == "Legs")
            ApplyGearCommand(action.type);
        else SetTarget(!deployed, true);
    }
    [KSPAction("Landing legs", KSPActionGroup.Gear)]
    public void GearAction(KSPActionParam action)
    {
        if (deploymentID != "Legs") return;
        // A craft may already have one of the original actions bound to Gear.
        // Let that binding handle the key once, including deliberate lower/raise bindings.
        if (((Actions["ToggleAction"].actionGroup | Actions["DeployAction"].actionGroup |
              Actions["RetractAction"].actionGroup) & action.group) != 0) return;
        ApplyGearCommand(action.type);
    }
    private void ApplyGearCommand(KSPActionType command)
    {
        bool lower = command == KSPActionType.Toggle ? !deployed : command == KSPActionType.Activate;
        // KSP dispatches vessel actions to each part, including each symmetry counterpart.
        if (lower != deployed) SetTarget(lower, false);
    }
    private void SetTarget(bool value, bool symmetry)
    {
        if (!value && deploymentID == "Legs" && HighLogic.LoadedSceneIsFlight)
            ModuleRWGroundTether.ReleaseForVessel(part.vessel, "Released for leg movement");
        deployed = value;
        if (symmetry)
            foreach (Part counterpart in part.symmetryCounterparts)
                foreach (ModuleRWGroundDeploy module in counterpart.FindModulesImplementing<ModuleRWGroundDeploy>())
                    if (module.deploymentID == deploymentID) module.SetTarget(value, false);
        ApplyPose();
        if (HighLogic.LoadedSceneIsEditor && EditorLogic.fetch != null)
            GameEvents.onEditorShipModified.Fire(EditorLogic.fetch.ship);
    }
    public void Update() { if (HighLogic.LoadedSceneIsEditor) Step(Time.deltaTime); }
    public void FixedUpdate() { if (HighLogic.LoadedSceneIsFlight) Step(Time.fixedDeltaTime); }
    // Reconcile after KSP's startup/crew UI binding as well as animation ticks.
    public void LateUpdate() { if (HighLogic.LoadedSceneIsFlight) ApplyAccess(); }
    private void Step(float dt)
    {
        if (bindings.Count == 0) return;
        deployment = Mathf.MoveTowards(deployment, deployed ? 1f : 0f, dt / Mathf.Max(.1f, duration));
        ApplyPose();
    }
    private void ApplyPose()
    {
        float t = deployment * deployment * (3f - 2f * deployment);
        foreach (Binding binding in bindings)
        {
            if (binding.transform == null) continue;
            binding.transform.localPosition = Vector3.Lerp(binding.endPosition, binding.startPosition, t);
            binding.transform.localRotation = Quaternion.Slerp(binding.endRotation, binding.startRotation, t);
            if(binding.fit!=null)binding.fit.Apply(binding.adjustment*t);
            // Legs keep physical contact through their travel. Stairs and the
            // ladder trigger are usable only when fully lowered, avoiding a
            // sweeping stair collider catching a Kerbal during deployment.
            foreach (Collider collider in binding.colliders)
                if (collider != null) collider.enabled = deploymentID == "Legs" || (deployed && deployment >= .99999f);
        }
        ApplyAccess();
        status = deployment >= .999f ? "Lowered" : deployment <= .001f ? "Raised" : deployed ? "Lowering" : "Raising";
        Events["Deploy"].active = !deployed; Events["Retract"].active = deployed;
    }
    private void ApplyAccess()
    {
        if (deploymentID != "Stairs" || part == null) return;
        bool open = deployed && deployment >= .99999f && hatch != null && bindings.Count > 0;
        if (hatch != null) hatch.enabled = open;
        if (open)
        {
            if (part.airlock == null || part.airlock.name == "Ground_EVA_Airlock") part.airlock = hatch.transform;
        }
        else if (part.airlock != null && part.airlock.name == "Ground_EVA_Airlock") part.airlock = null;
        if (!HighLogic.LoadedSceneIsFlight) return;
        // Portrait EVA checks NoAutoEVA, even with a disabled native trigger.
        // Own the lock only while required; preserve existing game/mod locks.
        if (!open && !evaLockOwned)
        {
            evaRestrictionBeforeLock = part.noAutoEVAAny;
            part.noAutoEVAAny = true;
            evaLockOwned = true;
        }
        else if (!open) part.noAutoEVAAny = true;
        else if (evaLockOwned)
        {
            part.noAutoEVAAny = evaRestrictionBeforeLock;
            evaLockOwned = false;
        }
    }
    public void OnDestroy()
    {
        foreach(Binding b in bindings)if(b.fit!=null)b.fit.Dispose();
        if (part != null && evaLockOwned) part.noAutoEVAAny = evaRestrictionBeforeLock;
        evaLockOwned = false;
    }
    public bool FitTerrain(Vector3 up,float dt,out bool ready)
    {
        ready=false;
        if(!deployed||deployment<.99999f||bindings.Count==0)return false;
        bool all=true,settled=true;
        foreach(Binding b in bindings)
        {
            if(b.fit==null||!b.fit.Valid){all=false;continue;}
            Vector3 surface;float target;
            if(deploymentID=="Legs")
            {
                Vector3 nominal=b.fit.WorldToe(0);
                if(!RWGroundSurface.Below(nominal,up,out surface)){all=false;continue;}
                float along=Vector3.Dot(b.transform.up,up);
                if(along<.95f){all=false;continue;}
                target=Vector3.Dot(surface-nominal,up)/along;
                if(target<-.65f||target>.35f){all=false;continue;}
            }
            else
            {
                // Pitch just the stair run around its landing; boarding trigger
                // and the top landing retain their original hull alignment.
                float low=-15f,high=15f;
                Vector3 a=b.fit.WorldToe(low),z=b.fit.WorldToe(high),sa,sz;
                if(!RWGroundSurface.Below(a,up,out sa)||!RWGroundSurface.Below(z,up,out sz)||Vector3.Dot(a-sa,up)<0||Vector3.Dot(z-sz,up)>0){all=false;continue;}
                for(int i=0;i<9;i++)
                {
                    float mid=(low+high)*.5f;Vector3 p=b.fit.WorldToe(mid);
                    if(!RWGroundSurface.Below(p,up,out surface)){all=false;break;}
                    if(Vector3.Dot(p-surface,up)>0)low=mid;else high=mid;
                }
                target=(low+high)*.5f;
            }
            b.adjustment=Mathf.MoveTowards(b.adjustment,target,dt*(deploymentID=="Legs"?.04f:1.5f));
            if(Mathf.Abs(b.adjustment-target)>(deploymentID=="Legs"?.006f:.12f))settled=false;
        }
        var values=new string[bindings.Count];for(int i=0;i<values.Length;i++)values[i]=bindings[i].adjustment.ToString("R",CultureInfo.InvariantCulture);
        supportFit=string.Join(";",values);ApplyPose();ready=all&&settled;return all;
    }
    public override string GetInfo() { return deploymentID == "Legs" ? "Animated telescoping supports; raised/lowered pose persists." : "Folding access stairs. Fully lower stairs before EVA or boarding."; }
}
