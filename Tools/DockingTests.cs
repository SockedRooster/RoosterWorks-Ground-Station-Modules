public static class DockingTest {
 static int checks;
 static void Check(bool b,string text){checks++;if(!b)throw new Exception(text);}
 static bool Locked(string n){return n.Contains("XFeed")||n.Contains("Crossfeed")||n=="ToggleStaging";}
 static Part Setup(string id,int count){
  var p=new Part{partInfo=new PartInfo{name=id,title="Owner"},vessel=new Vessel()};p.vessel.parts.Add(p);
  foreach(string key in new[]{"DisableCrossfeed","EnableCrossfeed","ToggleStaging","MakeReferenceToggle"}){p.Events.Add(new BaseEvent{name=key});p.Actions.Add(new BaseAction{name=key});}
  string[] ends=count==4?new[]{"right","left","front","back"}:count==1?new[]{"top"}:new[]{"top","bottom"};
  foreach(string key in ends){
   var n=new ModuleDockingNode{part=p,referenceAttachNode=key};
   foreach(string e in new[]{"EnableXFeed","DisableXFeed","ToggleStaging","Undock","Decouple","UndockSameVessel","MakeReferenceToggle","MakeReferenceTransform","SetAsTarget"})n.Events.Add(new BaseEvent{name=e});
   foreach(string a in new[]{"EnableXFeedAction","DisableXFeedAction","ToggleXFeedAction","ToggleStaging","UndockAction","DecoupleAction","MakeReferenceToggle"})n.Actions.Add(new BaseAction{name=a});
   foreach(string f in new[]{"crossfeed","stagingEnabled","acquireForceTweak","acquireForce","captureRange","dockingForce"})n.Fields.Add(new BaseField{name=f});
   var other=new Part{partInfo=new PartInfo{name="RW.GND.HAB",title="RoosterWorks Ground HAB - Habitation"},flightID=(uint)(100+p.Modules.Count)};
   n.otherNode=new ModuleDockingNode{part=other};p.vessel.parts.Add(other);p.nodes[key]=new AttachNode{attachedPart=other};p.Modules.Add(n);
  }
  var command=new ModuleCommand{part=p};command.Events.Add(new BaseEvent{name="MakeReferenceToggle"});command.Actions.Add(new BaseAction{name="MakeReference"});p.Modules.Add(command);
  var named=new ModuleDockingNodeNamed{part=p};named.Events.Add(new BaseEvent{name="renameDockingPort"});named.Fields.Add(new BaseField{name="portName"});p.Modules.Add(named);
  var habitat=new ModuleHabitat{part=p};habitat.Events.Add(new BaseEvent{name="ToggleHabitat"});habitat.Fields.Add(new BaseField{name="pressure"});p.Modules.Add(habitat);
  return p;
 }
 static void Dirty(Part p){
  p.fuelCrossFeed=false;p.stagingOn=true;
  foreach(var m in p.Modules){foreach(var e in m.Events)e.active=e.guiActive=e.guiActiveEditor=e.guiActiveUnfocused=true;foreach(var a in m.Actions){a.active=true;a.actionGroup=KSPActionGroup.Custom01;}foreach(var f in m.Fields)f.guiActive=f.guiActiveEditor=true;}
  foreach(var n in p.FindModulesImplementing<ModuleDockingNode>()){n.crossfeed=false;n.stagingEnabled=n.stagingToggleEnabledEditor=n.stagingToggleEnabledFlight=true;n.acquireForceTweak=12;}
  foreach(var e in p.Events)e.active=e.guiActive=e.guiActiveEditor=e.guiActiveUnfocused=true;
  foreach(var a in p.Actions){a.active=true;a.actionGroup=KSPActionGroup.Stage;}
 }
 static void Validate(Part p){
  bool command=p.partInfo.name.Replace('_','.')=="RW.GND.CMD";
  Check(p.fuelCrossFeed&&!p.stagingOn,"part crossfeed / staging");
  foreach(var e in p.Events)if(Locked(e.name)||(!command&&e.name=="MakeReferenceToggle"))Check(!e.active&&!e.guiActive&&!e.guiActiveEditor&&!e.guiActiveUnfocused,"part UI hidden");
  foreach(var a in p.Actions)if(Locked(a.name)||(!command&&a.name=="MakeReferenceToggle"))Check(!a.active&&a.actionGroup==KSPActionGroup.None,"part binding cleared");
  foreach(var n in p.FindModulesImplementing<ModuleDockingNode>()){
   Check(n.crossfeed&&!n.stagingEnabled&&!n.stagingToggleEnabledEditor&&!n.stagingToggleEnabledFlight,"port policy");
   Check(n.acquireRange==2.5f&&n.acquireForce==40&&n.acquireTorque==30&&n.acquireForceTweak==100,"strong locked attraction");
   Check(n.acquireMinFwdDot==.258819f&&n.captureMinFwdDot==.998f&&n.captureMaxRvel==.3f,"alignment and low-speed capture preserved");
   Check(n.minDistanceToReEngage>n.acquireRange,"release must clear attraction envelope before recapture");
   foreach(var e in n.Events){
    if(Locked(e.name)||e.name.StartsWith("MakeReference"))Check(!e.active&&!e.guiActive&&!e.guiActiveEditor&&!e.guiActiveUnfocused,"port clutter / control hidden");
    else {Check(e.active,"release and target actions retained");if(e.name!="SetAsTarget")Check(e.guiName=="Undock(RoosterWorks Ground HAB - Habitation)","connected part title on each release");}
   }
   foreach(var a in n.Actions)if(Locked(a.name)||a.name.StartsWith("MakeReference"))Check(!a.active&&a.actionGroup==KSPActionGroup.None,"port bindings hidden");else Check(a.active,"manual release bindings retained");
   foreach(var f in n.Fields)Check(!f.guiActive&&!f.guiActiveEditor,"force fields hidden");
  }
  var cm=p.FindModulesImplementing<ModuleCommand>()[0];Check(cm.Events[0].active==command&&cm.Actions[0].active==command,"only CMD command reference remains");
  var named=p.FindModulesImplementing<ModuleDockingNodeNamed>()[0];Check(!named.Events[0].active&&!named.Fields[0].guiActive&&!named.Fields[0].guiActiveEditor,"DPAI naming hidden without deleting module or names");
  var hab=p.FindModulesImplementing<ModuleHabitat>()[0];Check(hab.Events[0].active&&hab.Fields[0].guiActive,"unrelated habitat controls untouched");
 }
 public static void Run(){
  var missing=new ModuleRWGroundDocking();missing.OnLoad(new ConfigNode());missing.FixedUpdate();Check(true,"missing part safe");
  foreach(string name in new[]{"RW.GND.HAB","RW_GND_CMD","RW.GND.CMD","RW.GND.HUB","RW.GND.END.250.125"}){
   var p=Setup(name,name.Contains("HUB")?4:name.Contains("END")?1:2);var m=new ModuleRWGroundDocking{part=p};
   m.OnLoad(new ConfigNode());Validate(p);
   var acquisition=p.FindModulesImplementing<ModuleDockingNode>()[0];
   foreach(int degrees in new[]{0,15,30,45,60,74,75,76,90,120,180}){
    bool admitted=Math.Cos(degrees*Math.PI/180.0)>=acquisition.acquireMinFwdDot;
    Check(admitted==(degrees<=75),"wide approach admits modest/crooked angles and excludes backward faces: "+degrees);
   }
   Dirty(p);m.OnStart(StartState.None);Validate(p);Dirty(p);m.OnStartFinished(StartState.None);Validate(p);
   HighLogic.LoadedSceneIsEditor=true;HighLogic.LoadedSceneIsFlight=false;
   for(int i=0;i<8;i++){Dirty(p);m.LateUpdate();Validate(p);}
   HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;Dirty(p);m.FixedUpdate();Validate(p);Dirty(p);m.LateUpdate();Validate(p);
   var first=p.FindModulesImplementing<ModuleDockingNode>()[0];int calls=first.enables;m.LateUpdate();Check(first.enables==calls,"clean tick doesn't call crossfeed setter again");
   first.otherNode=null;m.LateUpdate();Check(first.Events.Find(e=>e.name=="Undock").guiName.Contains("Habitation"),"pre-attached node title fallback");
   first.dockedPartUId=p.nodes[first.referenceAttachNode].attachedPart.flightID;p.nodes[first.referenceAttachNode].attachedPart=null;m.LateUpdate();Check(first.Events.Find(e=>e.name=="Undock").guiName.Contains("Habitation"),"saved dock UID fallback");
   var target=p.vessel.parts[1];target.partInfo.title="Renamed connected part";m.LateUpdate();Check(first.Events.Find(e=>e.name=="Undock").guiName=="Undock(Renamed connected part)","connected part change refreshes label");
   first.dockedPartUId=0;first.Events.Find(e=>e.name=="Undock").active=false;m.LateUpdate();Check(!first.Events.Find(e=>e.name=="Undock").active,"never manufacture an undock action on a free port");
  }
  var unknown=Setup("RW.GND.CMD",2);unknown.partInfo=null;var guard=new ModuleRWGroundDocking{part=unknown};guard.OnLoad(new ConfigNode());Check(unknown.FindModulesImplementing<ModuleCommand>()[0].Events[0].active,"unknown prefab identity doesn't suppress command permanently");unknown.partInfo=new PartInfo{name="RW.GND.CMD"};guard.OnStart(StartState.None);Check(unknown.FindModulesImplementing<ModuleCommand>()[0].Events[0].active,"command survives prefab/start");
  var carrier=Setup("RW.SC.CARRIER.400",2);var carrierPort=carrier.FindModulesImplementing<ModuleDockingNode>()[0];new ModuleRWGroundDocking{part=carrier}.FixedUpdate();Check(carrierPort.acquireRange==.5f&&carrierPort.acquireForce==2,"capture-force tuning scoped to ground IDs");
  Console.WriteLine("PASS "+checks+" docking/menu assertions: 1/2/4 ports, normalized IDs, connected-part labels, CMD-only control, optional DPAI UI, force/alignment policy, recapture separation and repeated menu reloads");
 }
}
