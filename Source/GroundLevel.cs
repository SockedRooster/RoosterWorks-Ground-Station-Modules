using System;
using System.Collections.Generic;
using UnityEngine;

// One command station coordinates the connected vessel. All bodies receive the
// same limited angular acceleration; no part is teleported or independently
// rotated against its docking joints. Supports follow actual static surfaces.
public sealed class ModuleRWGroundLevel : PartModule
{
    [KSPField(isPersistant=true)] public bool leveling;
    [KSPField(isPersistant=true)] public bool resumeTether;
    [KSPField(guiActive=true,guiName="Station leveling")]public string levelStatus="Off";
    private float stable;
    [KSPEvent(guiActive=true,guiName="Auto-Level Station")]
    public void EnableLevel()
    {
        if(vessel==null||!vessel.Landed||vessel.Splashed){levelStatus="Land before leveling";return;}
        bool tether=false;
        foreach(ModuleRWGroundTether t in vessel.FindPartModulesImplementing<ModuleRWGroundTether>())if(t.tetherEnabled)tether=true;
        foreach(ModuleRWGroundLevel m in vessel.FindPartModulesImplementing<ModuleRWGroundLevel>())
        {m.leveling=true;m.resumeTether=tether;m.stable=0;}
        ModuleRWGroundTether.ReleaseForVessel(vessel,"Released for station leveling");
        foreach(ModuleRWGroundDeploy d in vessel.FindPartModulesImplementing<ModuleRWGroundDeploy>())d.Deploy();
        levelStatus="Lowering supports / stairs";
    }
    [KSPEvent(guiActive=true,guiName="Stop Auto-Leveling")]
    public void DisableLevel()
    {
        if(vessel!=null)foreach(ModuleRWGroundLevel m in vessel.FindPartModulesImplementing<ModuleRWGroundLevel>())
        {m.leveling=false;m.resumeTether=false;m.levelStatus="Off — holding support lengths";}
    }
    [KSPAction("Auto-Level Station")]public void LevelAction(KSPActionParam p){EnableLevel();}
    [KSPAction("Stop Auto-Leveling")]public void StopAction(KSPActionParam p){DisableLevel();}
    public void Update()
    {Events["EnableLevel"].active=!leveling;Events["DisableLevel"].active=leveling;}
    public void FixedUpdate()
    {
        if(!HighLogic.LoadedSceneIsFlight||!leveling||vessel==null)return;
        foreach(ModuleRWGroundLevel m in vessel.FindPartModulesImplementing<ModuleRWGroundLevel>())
            if(m.leveling){if(m!=this){levelStatus="Controlled by connected command station";return;}break;}
        if(!vessel.loaded||vessel.packed||TimeWarp.CurrentRateIndex!=0||(vessel.precalc!=null&&vessel.precalc.isEasingGravity))
        {stable=0;levelStatus="Paused during warp / ground physics";return;}
        if(!vessel.Landed||vessel.Splashed||vessel.mainBody==null||vessel.srf_velocity.magnitude>.35||
            (vessel.ctrlState!=null&&(vessel.ctrlState.mainThrottle>.01f||Math.Abs(vessel.ctrlState.wheelThrottle)>.01f)))
        {stable=0;levelStatus="Paused — station must be landed and still";return;}
        foreach(ModuleRWCollapsibleTube tube in vessel.FindPartModulesImplementing<ModuleRWCollapsibleTube>())
            if(Mathf.Abs(tube.extension-tube.targetExtension)>.0001f)
            {stable=0;levelStatus="Paused for crew tube movement";return;}
        foreach(ModuleRWGroundTether t in vessel.FindPartModulesImplementing<ModuleRWGroundTether>())
            if(t.tetherEnabled){levelStatus="Holding level — ground tether enabled";return;}
        Vector3 up=((Vector3)(part.transform.position-vessel.mainBody.position)).normalized;
        float tilt=Vector3.Angle(part.transform.up,up);
        if(tilt>8f){stable=0;levelStatus="Slope exceeds 8° leveling limit";return;}
        bool all=true,settled=true;int legs=0;
        foreach(ModuleRWGroundDeploy d in vessel.FindPartModulesImplementing<ModuleRWGroundDeploy>())
        {
            bool ready;
            if(d.deploymentID=="Legs")legs++;
            if(!d.FitTerrain(up,Time.fixedDeltaTime,out ready))all=false;
            if(!ready)settled=false;
        }
        if(legs==0||!all){stable=0;levelStatus="Waiting — supports deploying or terrain beyond travel";return;}
        // Gentle physics jacking: cap rotation to about 0.6 degrees/second.
        // Never accumulate large torques against an immovable assembly.
        Vector3 axis=Vector3.Cross(part.transform.up,up);
        var bodies=new HashSet<Rigidbody>();
        foreach(Part p in vessel.parts)
        {
            Rigidbody rb=p.Rigidbody;if(rb==null||rb.isKinematic||!bodies.Add(rb))continue;
            Vector3 lateralSpin=Vector3.ProjectOnPlane(rb.angularVelocity,up);
            Vector3 desired=Vector3.ClampMagnitude(axis*.35f,.010f);
            Vector3 alpha=Vector3.ClampMagnitude((desired-lateralSpin)*2f,.025f);
            Quaternion inertiaFrame=rb.rotation*rb.inertiaTensorRotation;
            Vector3 torque=inertiaFrame*Vector3.Scale(rb.inertiaTensor,Quaternion.Inverse(inertiaFrame)*alpha);
            rb.AddTorque(torque,ForceMode.Force);
        }
        if(tilt<.20f&&settled)stable+=Time.fixedDeltaTime;else stable=0;
        levelStatus=stable>2f?"Level — supports and stairs fitted":"Leveling supports and stairs";
        if(stable>2f&&resumeTether)
        {
            resumeTether=false;
            foreach(ModuleRWGroundTether t in vessel.FindPartModulesImplementing<ModuleRWGroundTether>()){t.EnableTether();break;}
        }
    }
    public override string GetInfo(){return "Auto-level the connected landed station and fit deployed legs/stairs to terrain. Feet extend up to 0.65 m or shorten by 0.35 m from the normal lowered pose; stairs: ±15°. Moderate slopes up to 8°. Existing tether releases during leveling and re-engages after settling.";}
}
