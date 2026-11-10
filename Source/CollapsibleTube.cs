using System;
using System.Collections.Generic;
using UnityEngine;

// An actuated stock connection: editor moves the cut branch; flight adjusts
// the FLEX-side joint anchors so PhysX pushes the attached branch normally.
public sealed class ModuleRWCollapsibleTube : PartModule
{
    [KSPField(isPersistant=true)] public float extension;
    [KSPField(isPersistant=true,guiActiveEditor=true,guiName="Extension",guiFormat="P1")]
    [UI_FloatRange(minValue=0f,maxValue=1f,stepIncrement=.001f)]
    public float targetExtension;
    [KSPField(guiActive=true,guiActiveEditor=true,guiName="Tube length",guiFormat="F3",guiUnits=" m")]
    public float currentLength=1.2f;
    [KSPField] public float duration=8f;
    [KSPField(guiActive=true,guiActiveEditor=true,guiName="Crew tube")]
    public string status="Collapsed";
    private Transform nose,bellows;
    private ModuleDockingNode movingPort;
    private bool subscribed, started, restoreJoint=true;
    public override void OnLoad(ConfigNode n){base.OnLoad(n);Bind();ApplyPose();}
    public override void OnStart(StartState s)
    {
        base.OnStart(s);Bind();ApplyPose();
        if(HighLogic.LoadedSceneIsFlight&&!subscribed)
        {GameEvents.onVesselGoOnRails.Add(OnRails);GameEvents.onVesselGoOffRails.Add(OffRails);subscribed=true;}
    }
    public override void OnStartFinished(StartState s){base.OnStartFinished(s);Bind();ApplyPose();started=true;}
    public override void OnSave(ConfigNode node){if(started)CommitPackedShape();base.OnSave(node);}
    // KSP Pack/Unpack reconstructs parts from orgPos/orgRot, not the live
    // actuated joint anchors. Commit the settled physical shape BEFORE Pack.
    private void CommitPackedShape()
    {
        if(!HighLogic.LoadedSceneIsFlight||vessel==null||!vessel.loaded||vessel.packed||vessel.rootPart==null)return;
        foreach(Part p in vessel.parts)if(p!=null)p.UpdateOrgPosAndRot(vessel.rootPart);
    }
    private void OnRails(Vessel target){if(target!=vessel)return;ApplyPose();CommitPackedShape();}
    private void OffRails(Vessel target)
    {
        if(target!=vessel)return;Bind();ApplyPose();ReinforceConnections();
        Part front=Front();if(front==null||part.Rigidbody==null)return;
        PartJoint link=front.parent==part?front.attachJoint:part.parent==front?part.attachJoint:null;
        if(link==null)return;
        // New joints must start without residual actuator preload. Both sides
        // refer to the same current end-fitting point; subsequent increments
        // still use the normal pushing actuator.
        foreach(ConfigurableJoint j in link.joints)
        {
            if(j==null||j.connectedBody==null)continue;
            Rigidbody host=j.GetComponent<Rigidbody>();
            if(host==null||(host!=part.Rigidbody&&j.connectedBody!=part.Rigidbody))continue;
            j.autoConfigureConnectedAnchor=false;
            j.anchor=host.transform.InverseTransformPoint(nose.position);
            j.connectedAnchor=j.connectedBody.transform.InverseTransformPoint(nose.position);
        }
    }
    public void OnDestroy()
    {if(subscribed){GameEvents.onVesselGoOnRails.Remove(OnRails);GameEvents.onVesselGoOffRails.Remove(OffRails);subscribed=false;}}
    private void Bind()
    {
        if(part==null)return;
        nose=part.FindModelTransform("RW_TubeNose");bellows=part.FindModelTransform("RW_TubeBellows");movingPort=null;
        foreach(ModuleDockingNode p in part.FindModulesImplementing<ModuleDockingNode>())if(p.referenceAttachNode=="top"){movingPort=p;break;}
    }
    private void Controls()
    {
        foreach(string key in new[]{"Extend","Collapse"})if(Events.Contains(key)&&Events[key]!=null)
        {Events[key].active=true;Events[key].guiActive=true;Events[key].guiActiveEditor=true;}
    }
    [KSPEvent(guiActive=true,guiActiveEditor=true,guiName="Extend Crew Tube")]
    public void Extend(){SetTarget(1);}
    [KSPEvent(guiActive=true,guiActiveEditor=true,guiName="Collapse Crew Tube")]
    public void Collapse(){SetTarget(0);}
    [KSPAction("Extend Crew Tube")]public void ExtendAction(KSPActionParam p){Extend();}
    [KSPAction("Collapse Crew Tube")]public void CollapseAction(KSPActionParam p){Collapse();}
    private void SetTarget(float value)
    {
        targetExtension=value;
        if(HighLogic.LoadedSceneIsFlight&&vessel!=null)ModuleRWGroundTether.ReleaseForVessel(vessel,"Released for crew tube movement");
        ApplyPose();
    }
    public void Update(){if(nose==null||bellows==null||movingPort==null)Bind();Controls();if(HighLogic.LoadedSceneIsEditor)Step(Time.deltaTime);}
    public void LateUpdate(){ApplyPose();}
    public void FixedUpdate()
    {
        if(!HighLogic.LoadedSceneIsFlight||part==null)return;
        if(vessel!=null&&(!vessel.loaded||vessel.packed||TimeWarp.CurrentRateIndex!=0))return;
        if(vessel!=null&&vessel.precalc!=null&&vessel.precalc.isEasingGravity)return;
        if(restoreJoint){OffRails(vessel);restoreJoint=false;}
        ReinforceConnections();
        Step(Time.fixedDeltaTime);
    }
    private void ReinforceConnections()
    {
        if(part==null||part.Rigidbody==null)return;
        // Cover either tree orientation and newly created docking joints.
        // Never alter unrelated joints elsewhere in the connected assembly.
        var links=new HashSet<PartJoint>();
        if(part.attachJoint!=null)links.Add(part.attachJoint);
        foreach(Part neighbor in Neighbors(part))
            if(neighbor.attachJoint!=null)links.Add(neighbor.attachJoint);
        foreach(PartJoint link in links)
        {
            bool connected=false;
            foreach(ConfigurableJoint j in link.joints)
            {
                if(j==null||!(j.GetComponent<Rigidbody>()==part.Rigidbody||j.connectedBody==part.Rigidbody))continue;
                connected=true;
                // Rigid end fittings; extension still moves the joint anchor.
                j.xMotion=j.yMotion=j.zMotion=ConfigurableJointMotion.Locked;
                j.angularXMotion=j.angularYMotion=j.angularZMotion=ConfigurableJointMotion.Locked;
                j.projectionMode=JointProjectionMode.PositionAndRotation;
                j.projectionDistance=.02f;j.projectionAngle=1f;
            }
            // Use KSP's public API: its own cached break thresholds must also
            // change, rather than changing only the Unity Joint properties.
            if(connected)link.SetBreakingForces(3500f,3500f);
        }
    }
    private Part Front()
    {
        AttachNode a=part.FindAttachNode("top");if(a!=null&&a.attachedPart!=null)return a.attachedPart;
        if(movingPort!=null&&movingPort.otherNode!=null)return movingPort.otherNode.part;
        if(movingPort!=null&&movingPort.dockedPartUId!=0&&vessel!=null)
            foreach(Part p in vessel.parts)if(p.flightID==movingPort.dockedPartUId)return p;
        return null;
    }
    private IEnumerable<Part> Neighbors(Part p)
    {
        if(p.parent!=null)yield return p.parent;
        foreach(Part c in p.children)if(c!=null)yield return c;
        foreach(ModuleDockingNode d in p.FindModulesImplementing<ModuleDockingNode>())if(d.otherNode!=null&&d.otherNode.part!=null)yield return d.otherNode.part;
    }
    private bool Branch(Part front,out HashSet<Part> branch)
    {
        branch=new HashSet<Part>();var queue=new Queue<Part>();queue.Enqueue(front);
        AttachNode rear=part.FindAttachNode("bottom");if(rear!=null&&rear.attachedPart==front)return false;
        foreach(ModuleDockingNode d in part.FindModulesImplementing<ModuleDockingNode>())
            if(d.referenceAttachNode!="top"&&d.otherNode!=null&&d.otherNode.part==front)return false;
        while(queue.Count>0)
        {
            Part p=queue.Dequeue();if(!branch.Add(p))continue;
            if(p==part)return false;
            foreach(Part n in Neighbors(p))
            {if(p==front&&n==part)continue;if(!branch.Contains(n))queue.Enqueue(n);}
        }
        return true;
    }
    private List<Part> EditorTree()
    {
        Part root=part;var parents=new HashSet<Part>();
        while(root.parent!=null&&parents.Add(root))root=root.parent;
        var result=new List<Part>();var seen=new HashSet<Part>();var stack=new Stack<Part>();stack.Push(root);
        while(stack.Count>0){Part p=stack.Pop();if(!seen.Add(p))continue;result.Add(p);for(int i=p.children.Count-1;i>=0;i--)if(p.children[i]!=null)stack.Push(p.children[i]);}
        return result;
    }
    private void MoveEditor(HashSet<Part> branch,Vector3 delta)
    {
        // Snapshot before moving any parent, then restore fixed-side positions.
        // This also supports a moving-end parent above FLEX in the editor tree.
        List<Part> all=EditorTree();var positions=new List<Vector3>();
        foreach(Part p in all)positions.Add(p.transform.position+(branch.Contains(p)?delta:Vector3.zero));
        for(int i=0;i<all.Count;i++)all[i].transform.position=positions[i];
    }
    private bool DriveJoint(Part front,Vector3 delta)
    {
        PartJoint link=front.parent==part?front.attachJoint:part.parent==front?part.attachJoint:null;
        if(link==null||part.Rigidbody==null||part.Rigidbody.isKinematic){status="Waiting for connected module physics";return false;}
        // Wait for the previous increment to settle, rather than accumulating
        // separation against a blocked payload or crossed external struts.
        Transform peer=null;
        if(movingPort!=null&&movingPort.otherNode!=null)
            peer=front.FindModelTransform(movingPort.otherNode.nodeTransformName);
        else
        {
            AttachNode node=front.FindAttachNodeByPart(part);
            if(node!=null&&Vector3.Distance(nose.position,front.transform.TransformPoint(node.position))>.15f)
            {status="Waiting for connected assembly to follow";return false;}
        }
        if(peer!=null&&Vector3.Distance(nose.position,peer.position)>.15f)
        {status="Waiting for connected assembly to follow";return false;}
        var matches=new List<ConfigurableJoint>();
        foreach(ConfigurableJoint j in link.joints)
            if(j!=null&&(j.GetComponent<Rigidbody>()==part.Rigidbody||j.connectedBody==part.Rigidbody))matches.Add(j);
        if(matches.Count==0){status="Waiting for moving-end joint";return false;}
        foreach(ConfigurableJoint j in matches)
        {
            j.autoConfigureConnectedAnchor=false;
            if(j.GetComponent<Rigidbody>()==part.Rigidbody)j.anchor+=part.Rigidbody.transform.InverseTransformVector(delta);
            else j.connectedAnchor+=part.Rigidbody.transform.InverseTransformVector(delta);
            if(j.connectedBody!=null)j.connectedBody.WakeUp();
            Rigidbody host=j.GetComponent<Rigidbody>();if(host!=null)host.WakeUp();
        }
        return true;
    }
    private void Step(float dt)
    {
        if(part==null||nose==null||bellows==null)return;
        Normalize();if(extension==targetExtension){ApplyPose();return;}
        float next=Mathf.MoveTowards(extension,targetExtension,dt/Mathf.Max(.1f,duration));
        Vector3 delta=part.transform.TransformVector(new Vector3(2.8f*(next-extension),0,0));
        Part front=Front();HashSet<Part> branch=null;
        if(front!=null)
        {
            if(!Branch(front,out branch)){status="Open a connection loop before resizing";return;}
            if(HighLogic.LoadedSceneIsEditor)MoveEditor(branch,delta);
            else
            {
                ModuleRWGroundTether.ReleaseForVessel(vessel,"Released for crew tube movement");
                if(!DriveJoint(front,delta))return;
            }
        }
        else if(movingPort!=null&&((movingPort.state??"").IndexOf("Acquire",StringComparison.OrdinalIgnoreCase)>=0||movingPort.dockedPartUId!=0))
        {status="Waiting for docking capture to finish";return;}
        extension=next;ApplyPose();
        if(HighLogic.LoadedSceneIsEditor&&EditorLogic.fetch!=null)GameEvents.onEditorShipModified.Fire(EditorLogic.fetch.ship);
    }
    private void Normalize()
    {
        if(float.IsNaN(extension)||float.IsInfinity(extension))extension=0;
        if(float.IsNaN(targetExtension)||float.IsInfinity(targetExtension))targetExtension=extension;
        extension=Mathf.Clamp01(extension);targetExtension=Mathf.Clamp01(targetExtension);
    }
    private void ApplyPose()
    {
        Controls();if(part==null||nose==null||bellows==null)return;Normalize();
        currentLength=1.2f+2.8f*extension;
        float x=.6f+2.8f*extension;nose.localPosition=new Vector3(x,0,0);bellows.localScale=new Vector3((.9f+2.8f*extension)/.9f,1,1);
        AttachNode a=part.FindAttachNode("top");if(a!=null){a.position=new Vector3(x,0,0);a.originalPosition=a.position;}
        status=extension>=.99999f?"Extended (4.0 m)":extension<=.00001f?"Collapsed (1.2 m)":extension==targetExtension?"Holding intermediate length":targetExtension>extension?"Extending / pushing connected modules":"Collapsing / drawing connected modules";
    }
    public override string GetInfo(){return "Sealed 2.5 m passage; 1.2–4 m. VAB Extension slider: 0–100% in 0.1% steps (2.8 mm of travel); live length readout. Saved intermediate lengths persist. Moving end pushes/draws connected modules. Tethers release for motion. Open closed connection loops before resizing.";}
}
