public static class TubeMotionTest {
 static int checks;static void Check(bool v,string m){checks++;if(!v)throw new Exception(m);}static void Near(float a,float b,string m){Check(Math.Abs(a-b)<.0003,m+" "+a+" / "+b);}
 static ModuleRWCollapsibleTube Tube(float t=0){var p=new Part();p.nodes["top"]=new AttachNode();p.nodes["bottom"]=new AttachNode{position=new UnityEngine.Vector3(-.6f,0,0)};p.transforms["RW_TubeNose"]=new UnityEngine.Transform{parent=p.transform};p.transforms["RW_TubeBellows"]=new UnityEngine.Transform{parent=p.transform};p.modules.Add(new ModuleDockingNode{part=p,referenceAttachNode="top",nodeTransformName="RW_TubeNose"});var m=new ModuleRWCollapsibleTube{part=p,extension=t,targetExtension=t};m.OnLoad(new ConfigNode());m.OnStart(StartState.None);m.OnStartFinished(StartState.None);return m;}
 static Part Attach(ModuleRWCollapsibleTube m,bool hostTube=false){var p=m.part;var front=new Part{parent=p,vessel=p.vessel};p.children.Add(front);front.transform.position=new UnityEngine.Vector3(1.2f+2.8f*m.extension,0,0);p.nodes["top"].attachedPart=front;front.nodes["rear"]=new AttachNode{attachedPart=p,position=new UnityEngine.Vector3(-.6f,0,0)};front.attachJoint=new PartJoint();front.attachJoint.joints.Add(new UnityEngine.ConfigurableJoint{host=hostTube?p.Rigidbody:front.Rigidbody,connectedBody=hostTube?front.Rigidbody:p.Rigidbody});return front;}
 static void Pose(ModuleRWCollapsibleTube m,float t){Near(m.extension,t,"saved extension");Near(m.part.transforms["RW_TubeNose"].localPosition.x,.6f+2.8f*t,"moving nose");Near(m.part.nodes["top"].position.x,.6f+2.8f*t,"stack node");Near(m.part.nodes["bottom"].position.x,-.6f,"fixed end");Near(m.part.transforms["RW_TubeBellows"].localScale.x,(.9f+2.8f*t)/.9f,"bellows contact hull");}
 static void Tick(ModuleRWCollapsibleTube m,int n=500){for(int i=0;i<n;i++)if(HighLogic.LoadedSceneIsEditor)m.Update();else m.FixedUpdate();}
 public static void Run(){
 HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;
 // Strengthening runs while idle, covers both ends/tree orientations, and
 // catches joints recreated by docking without touching unrelated links.
 var reinforced=Tube();var rf=Attach(reinforced);var rearPart=new Part();
 reinforced.part.parent=rearPart;rearPart.children.Add(reinforced.part);
 reinforced.part.nodes["bottom"].attachedPart=rearPart;
 reinforced.part.attachJoint=new PartJoint();
 reinforced.part.attachJoint.joints.Add(new UnityEngine.ConfigurableJoint{host=reinforced.part.Rigidbody,connectedBody=rearPart.Rigidbody});
 rearPart.attachJoint=new PartJoint();rearPart.attachJoint.joints.Add(new UnityEngine.ConfigurableJoint{host=rearPart.Rigidbody,connectedBody=new Part().Rigidbody});
 Tick(reinforced,1);
 foreach(var link in new[]{reinforced.part.attachJoint,rf.attachJoint}){
  Near(link.force,3500,"reinforced connection break force");Near(link.torque,3500,"reinforced connection break torque");
  var j=link.joints[0];Check(j.xMotion==UnityEngine.ConfigurableJointMotion.Locked&&j.yMotion==UnityEngine.ConfigurableJointMotion.Locked&&j.zMotion==UnityEngine.ConfigurableJointMotion.Locked,"linear end fitting rigid");
  Check(j.angularXMotion==UnityEngine.ConfigurableJointMotion.Locked&&j.angularYMotion==UnityEngine.ConfigurableJointMotion.Locked&&j.angularZMotion==UnityEngine.ConfigurableJointMotion.Locked,"angular end fitting rigid");
  Check(j.projectionMode==UnityEngine.JointProjectionMode.PositionAndRotation,"joint projection");Near(j.projectionDistance,.02f,"projection gap tolerance");Near(j.projectionAngle,1,"projection angular tolerance");
 }
 Check(rearPart.attachJoint.strengthCalls==0,"unrelated connection untouched");
 var rebuilt=new PartJoint();rebuilt.joints.Add(new UnityEngine.ConfigurableJoint{host=rf.Rigidbody,connectedBody=reinforced.part.Rigidbody});rf.attachJoint=rebuilt;
 Tick(reinforced,1);Near(rebuilt.force,3500,"recreated dock strengthened");
 foreach(float saved in new[]{0f,.25f,.5f,.75f,1f}){var m=Tube(saved);Pose(m,saved);}
 var free=Tube();free.Extend();Tick(free);Pose(free,1);free.Collapse();Tick(free);Pose(free,0);
 foreach(bool hostTube in new[]{false,true}){
  var m=Tube();var front=Attach(m,hostTube);var joint=front.attachJoint.joints[0];m.FixedUpdate();float baseline=hostTube?joint.anchor.x:joint.connectedAnchor.x;m.Extend();float last=baseline;
  for(int i=0;i<450;i++){
   float old=front.transform.position.x;m.FixedUpdate();Near(front.transform.position.x,old,"flight never teleports payload");float anchor=hostTube?joint.anchor.x:joint.connectedAnchor.x;float change=anchor-last;last=anchor;front.transform.position+=new UnityEngine.Vector3(change,0,0);
  }
  Pose(m,1);Near(front.transform.position.x,4f,"physical solver follows moving joint rest point");Near(last-baseline,2.8f,"full extension joint travel");Check(!joint.autoConfigureConnectedAnchor,"joint explicit anchor mode");Check(joint.host.wakes>0&&joint.connectedBody.wakes>0,"physics bodies woken");
  m.Collapse();for(int i=0;i<450;i++){m.FixedUpdate();float anchor=hostTube?joint.anchor.x:joint.connectedAnchor.x;front.transform.position+=new UnityEngine.Vector3(anchor-last,0,0);last=anchor;}Pose(m,0);Near(front.transform.position.x,1.2f,"physical retraction draws connected assembly");
 }
 var stalled=Tube();var stuck=Attach(stalled);stalled.Extend();Tick(stalled);Check(stalled.extension>0&&stalled.extension<.1f,"blocked assembly must not accumulate unbounded joint stretch");Check(stalled.status.Contains("follow"),"blocked payload wait status");
 HighLogic.LoadedSceneIsEditor=true;HighLogic.LoadedSceneIsFlight=false;
 var editor=Tube();var branch=Attach(editor);var child=new Part{parent=branch};branch.children.Add(child);child.transform.position=new UnityEngine.Vector3(2.5f,0,0);var rear=new Part();rear.transform.position=new UnityEngine.Vector3(-2,0,0);editor.part.parent=rear;rear.children.Add(editor.part);editor.part.nodes["bottom"].attachedPart=rear;editor.Extend();Tick(editor);Pose(editor,1);Near(branch.transform.position.x,4,"editor connected module pushed");Near(child.transform.position.x,5.3f,"editor entire attached branch moves");Near(rear.transform.position.x,-2,"editor rear assembly fixed");Near(editor.part.transform.position.x,0,"tube reference fixed");editor.Collapse();Tick(editor);Near(branch.transform.position.x,1.2f,"editor retraction");Check(GameEvents.onEditorShipModified.calls>0,"craft position updates published");
 var reversed=Tube();var movingParent=new Part();reversed.part.parent=movingParent;movingParent.children.Add(reversed.part);reversed.part.nodes["top"].attachedPart=movingParent;reversed.part.transform.parent=movingParent.transform;reversed.Extend();Tick(reversed);Pose(reversed,1);Near(movingParent.transform.position.x,2.8f,"parent on moving end moves");Near(reversed.part.transform.position.x,0,"fixed tube restored after moving its editor parent");
 var loop=Tube();var f=Attach(loop);var r=new Part();loop.part.parent=r;r.children.Add(loop.part);loop.part.nodes["bottom"].attachedPart=r;var a=new ModuleDockingNode{part=f};var b=new ModuleDockingNode{part=r};a.otherNode=b;b.otherNode=a;f.modules.Add(a);r.modules.Add(b);loop.Extend();Tick(loop);Pose(loop,0);Check(loop.status.Contains("loop"),"closed rigid loop must explain stop");
 foreach(string pause in new[]{"packed","unloaded","warp"}){HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;var m=Tube();Attach(m);m.Extend();if(pause=="packed")m.vessel.packed=true;if(pause=="unloaded")m.vessel.loaded=false;if(pause=="warp")TimeWarp.CurrentRateIndex=1;Tick(m);Pose(m,0);TimeWarp.CurrentRateIndex=0;}
 var acquire=Tube();acquire.part.FindModulesImplementing<ModuleDockingNode>()[0].state="Acquire";acquire.Extend();Tick(acquire);Pose(acquire,0);Check(acquire.status.Contains("capture"),"capture cannot move before joint exists");acquire.part.FindModulesImplementing<ModuleDockingNode>()[0].state="Ready";Tick(acquire);Pose(acquire,1);
 var missing=Tube();var mf=Attach(missing);mf.attachJoint=null;missing.Extend();Tick(missing);Pose(missing,0);Check(missing.status.Contains("physics"),"missing joint waits");
 foreach(float bad in new[]{float.NaN,float.PositiveInfinity,-2f,4f}){var m=Tube(bad);Check(m.extension>=0&&m.extension<=1,"invalid save clamped");}
 var restore=Tube(.5f);var loadFront=Attach(restore);float initial=loadFront.transform.position.x;restore.OnStartFinished(StartState.None);Near(loadFront.transform.position.x,initial,"reload never shifts connected assembly");Pose(restore,.5f);restore.Events["Extend"].active=false;restore.LateUpdate();Check(restore.Events["Extend"].active&&restore.Events["Extend"].guiActive&&restore.Events["Extend"].guiActiveEditor,"controls persist in both scenes");Check(ModuleRWGroundTether.releases>0,"tethers released for driven motion");
 new ModuleRWCollapsibleTube().OnStart(StartState.None);new ModuleRWCollapsibleTube().FixedUpdate();Check(true,"missing part safe");
 // The VAB slider writes the existing saved target. Exercise the exact Update
 // path, rather than a parallel test-only resizing implementation.
 var field=typeof(ModuleRWCollapsibleTube).GetField("targetExtension");
 var ui=(UI_FloatRange)Attribute.GetCustomAttribute(field,typeof(UI_FloatRange));
 var gui=(KSPField)Attribute.GetCustomAttribute(field,typeof(KSPField));
 Check(gui.isPersistant&&gui.guiActiveEditor&&!gui.guiActive&&gui.guiFormat=="P1","persistent editor-only percentage slider");
 Near(ui.minValue,0,"slider lower limit");Near(ui.maxValue,1,"slider upper limit");Near(ui.stepIncrement,.001f,"0.1 percent adjustment precision");
 HighLogic.LoadedSceneIsEditor=true;HighLogic.LoadedSceneIsFlight=false;
 foreach(float selected in new[]{.001f,.137f,.333f,.501f,.999f}){
  var m=Tube();var front=Attach(m);var partialChild=new Part{parent=front};front.children.Add(partialChild);partialChild.transform.position=new UnityEngine.Vector3(2.5f,0,0);
  m.targetExtension=selected;Tick(m);Pose(m,selected);Near(m.currentLength,1.2f+2.8f*selected,"live length readout");
  Near(front.transform.position.x,1.2f+2.8f*selected,"slider moves connected front");Near(partialChild.transform.position.x,2.5f+2.8f*selected,"slider moves entire branch");Near(m.part.transform.position.x,0,"fixed tube reference");
  float stable=front.transform.position.x;m.OnStartFinished(StartState.None);Tick(m,50);Near(front.transform.position.x,stable,"menu/reload leaves settled partial length fixed");Pose(m,selected);
  // Save/load reconstructs both persistent fields without resetting to an end stop.
  var restored=Tube(m.extension);Pose(restored,selected);Near(restored.currentLength,m.currentLength,"restored length readout");
  m.targetExtension=.079f;Tick(m);Pose(m,.079f);Near(front.transform.position.x,1.2f+2.8f*.079f,"partial retraction");
  m.Extend();Tick(m);Pose(m,1);m.Collapse();Tick(m);Pose(m,0);
 }
 var reversePartial=Tube(.2f);var parentPartial=new Part();reversePartial.part.parent=parentPartial;parentPartial.children.Add(reversePartial.part);reversePartial.part.nodes["top"].attachedPart=parentPartial;reversePartial.part.transform.parent=parentPartial.transform;
 reversePartial.targetExtension=.6f;Tick(reversePartial);Pose(reversePartial,.6f);Near(parentPartial.transform.position.x,1.12f,"partial extension moves parent branch");Near(reversePartial.part.transform.position.x,0,"partial extension keeps fixed side");
 var partialLoop=Tube(.25f);var lf=Attach(partialLoop);var lr=new Part();partialLoop.part.parent=lr;lr.children.Add(partialLoop.part);partialLoop.part.nodes["bottom"].attachedPart=lr;
 var ld1=new ModuleDockingNode{part=lf};var ld2=new ModuleDockingNode{part=lr};ld1.otherNode=ld2;ld2.otherNode=ld1;lf.modules.Add(ld1);lr.modules.Add(ld2);partialLoop.targetExtension=.4f;Tick(partialLoop);Pose(partialLoop,.25f);Check(partialLoop.status.Contains("loop"),"partial slider still rejects closed loops");
 HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;
 foreach(float selected in new[]{.137f,.5f,1f}){
  var m=Tube(selected);var warpFront=Attach(m);var v=m.vessel;v.rootPart=m.part;v.parts.Add(m.part);v.parts.Add(warpFront);var tail=new Part{vessel=v};tail.transform.position=new UnityEngine.Vector3(8f,1,2);v.parts.Add(tail);
  float before=warpFront.transform.position.x;var other=Tube(.1f);float otherPose=other.extension;
  for(int cycle=0;cycle<12;cycle++){
   GameEvents.onVesselGoOnRails.Fire(v);Near(warpFront.orgPos.x,before,"rails snapshots extended payload");Near(tail.orgPos.x,8,"rails snapshots entire assembly");
   v.packed=true;TimeWarp.CurrentRateIndex=5;warpFront.transform.position=m.part.transform.TransformPoint(warpFront.orgPos);tail.transform.position=m.part.transform.TransformPoint(tail.orgPos);
   m.part.transforms["RW_TubeBellows"].localScale=new UnityEngine.Vector3(1,1,1);m.LateUpdate();Tick(m,5);Pose(m,selected);Near(warpFront.transform.position.x,before,"no packed collapse");
   v.packed=false;TimeWarp.CurrentRateIndex=0;warpFront.attachJoint=new PartJoint();var j=new UnityEngine.ConfigurableJoint{host=warpFront.Rigidbody,connectedBody=m.part.Rigidbody};warpFront.attachJoint.joints.Add(j);
   GameEvents.onVesselGoOffRails.Fire(v);Near(warpFront.transform.TransformPoint(j.anchor).x,m.part.transform.TransformPoint(j.connectedAnchor).x,"rebuilt joint zero preload");Tick(m,2);Near(warpFront.transform.position.x,before,"no unpack jump");Pose(m,selected);Near(other.extension,otherPose,"unrelated vessel preserved");
  }
  m.OnSave(new ConfigNode());Near(warpFront.orgPos.x,before,"save keeps extended assembly");m.OnDestroy();other.OnDestroy();
 }
 Console.WriteLine("PASS "+checks+" connected-tube assertions: partial editor slider/precision/readout/save/reopen/parent branches; full travel, both joint orientations, solver-driven push/retraction, no flight teleport, closed loops, stalled payloads, capture, reload, warp and controls");
 }
}

