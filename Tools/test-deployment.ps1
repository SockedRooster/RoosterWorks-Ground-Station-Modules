$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/GroundDeploy.cs') -Raw
$doubles=@'
namespace UnityEngine {
 public struct Vector3 {public float x,y,z;public Vector3(float a,float b,float c){x=a;y=b;z=c;}public static Vector3 Lerp(Vector3 a,Vector3 b,float t){return new Vector3(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,a.z+(b.z-a.z)*t);}}
 public struct Quaternion {public Vector3 angles;public static Quaternion identity=new Quaternion();public static Quaternion Euler(Vector3 v){return new Quaternion{angles=v};}public static Quaternion Slerp(Quaternion a,Quaternion b,float t){return Euler(Vector3.Lerp(a.angles,b.angles,t));}}
 public class Collider {public bool enabled=true,isTrigger;public string name;public Transform transform;public bool CompareTag(string s){return s=="Airlock"&&name=="Ground_EVA_Airlock";}}
 public class Transform {public string name;public Vector3 localPosition;public Quaternion localRotation=Quaternion.identity;public Collider[] colliders={new Collider()};public T[] GetComponentsInChildren<T>(bool include){return (T[])(object)colliders;}}
 public static class Mathf {public static float Clamp01(float p){return Math.Max(0,Math.Min(1,p));}public static float Max(float a,float b){return Math.Max(a,b);}public static float MoveTowards(float p,float target,float step){return Math.Abs(target-p)<=step?target:p+Math.Sign(target-p)*step;}}
 public static class Time {public static float deltaTime=.05f,fixedDeltaTime=.05f;}
 public static class Debug {public static void LogError(string s){throw new Exception(s);}}
}
public enum StartState {None}
public class KSPActionParam {}
public class KSPField:Attribute {public bool isPersistant,guiActive,guiActiveEditor;public string guiName;}
public class KSPEvent:Attribute {public bool guiActive,guiActiveEditor;public string guiName;}
public class KSPAction:Attribute {public KSPAction(string s){}}
public class Control {public string guiName;public bool active=true;}
public class PartModule {public Part part;public Dictionary<string,Control> Fields=new Dictionary<string,Control>{{"status",new Control()}};public Dictionary<string,Control> Events=new Dictionary<string,Control>{{"Deploy",new Control()},{"Retract",new Control()}};public Dictionary<string,Control> Actions=new Dictionary<string,Control>{{"DeployAction",new Control()},{"RetractAction",new Control()},{"ToggleAction",new Control()}};public virtual void OnStart(StartState s){}public virtual void OnLoad(ConfigNode n){}public virtual string GetInfo(){return "";}}
public static class HighLogic {public static bool LoadedSceneIsEditor=true,LoadedSceneIsFlight=false;}
public class ConfigNode {public string name;public Dictionary<string,string> values=new Dictionary<string,string>();public List<ConfigNode> children=new List<ConfigNode>();public ConfigNode(string n){name=n;}public void AddValue(string k,string v){values[k]=v;}public string GetValue(string k){return values.ContainsKey(k)?values[k]:null;}public void AddNode(ConfigNode n){children.Add(n);}public ConfigNode[] GetNodes(string n){return children.FindAll(x=>x.name==n).ToArray();}}
public class PartInfo {public ConfigNode partConfig=new ConfigNode("PART");}
public class Vessel {} public static class ModuleRWGroundTether {public static int releases; public static void ReleaseForVessel(Vessel v,string reason){releases++;}} public class Part {public Vessel vessel=new Vessel();public bool noAutoEVAAny;public UnityEngine.Transform airlock;public UnityEngine.Collider hatch=new UnityEngine.Collider{name="Ground_EVA_Airlock",isTrigger=true,transform=new UnityEngine.Transform{name="Ground_EVA_Airlock"}};public T[] GetComponentsInChildren<T>(bool include){return (T[])(object)(hatch==null?new UnityEngine.Collider[0]:new[]{hatch});}public string name="ground test";public PartInfo partInfo=new PartInfo();public List<Part> symmetryCounterparts=new List<Part>();public Dictionary<string,UnityEngine.Transform> transforms=new Dictionary<string,UnityEngine.Transform>();public List<ModuleRWGroundDeploy> modules=new List<ModuleRWGroundDeploy>();public UnityEngine.Transform[] FindModelTransforms(string n){return transforms.ContainsKey(n)?new[]{transforms[n]}:new UnityEngine.Transform[0];}public List<T> FindModulesImplementing<T>(){var result=new List<T>();foreach(var m in modules)result.Add((T)(object)m);return result;}}
public class ShipEvent {public void Fire(object ship){}}
public static class GameEvents {public static ShipEvent onEditorShipModified=new ShipEvent();}
public class EditorLogic {public static EditorLogic fetch=new EditorLogic();public object ship=new object();}
public static class GroundDeployTest {
 static void Check(bool condition,string message){if(!condition)throw new Exception(message);}
 static UnityEngine.Vector3 Read(string value){var s=value.Split(',');return new UnityEngine.Vector3(float.Parse(s[0],CultureInfo.InvariantCulture),float.Parse(s[1],CultureInfo.InvariantCulture),float.Parse(s[2],CultureInfo.InvariantCulture));}
 static bool Close(UnityEngine.Vector3 a,UnityEngine.Vector3 b){return Math.Abs(a.x-b.x)+Math.Abs(a.y-b.y)+Math.Abs(a.z-b.z)<.00001f;}
 static ModuleRWGroundDeploy Setup(string id,ConfigNode cfg,float progress,bool target,bool hatchPresent=true,bool restricted=false,bool owned=false,bool prior=false){var p=new Part{noAutoEVAAny=restricted};if(!hatchPresent)p.hatch=null;p.partInfo.partConfig.AddNode(cfg);foreach(var n in cfg.GetNodes("TRANSFORM"))p.transforms[n.GetValue("name")]=new UnityEngine.Transform{localPosition=new UnityEngine.Vector3(99,99,99)};var m=new ModuleRWGroundDeploy{part=p,deploymentID=id,deployment=progress,deployed=target,evaLockOwned=owned,evaRestrictionBeforeLock=prior};p.modules.Add(m);m.OnLoad(new ConfigNode("MODULE"));m.OnStart(StartState.None);return m;}
 static void Pose(ModuleRWGroundDeploy m,ConfigNode cfg){float s=m.deployment*m.deployment*(3-2*m.deployment);foreach(var n in cfg.GetNodes("TRANSFORM")){var t=m.part.transforms[n.GetValue("name")];Check(Close(t.localPosition,UnityEngine.Vector3.Lerp(Read(n.GetValue("retractPosition")),Read(n.GetValue("deployPosition")),s)),"pose/config mismatch");Check(Close(t.localRotation.angles,UnityEngine.Vector3.Lerp(Read(n.GetValue("retractEuler")),new UnityEngine.Vector3(),s)),"rotation mismatch");Check(t.colliders[0].enabled==(m.deploymentID=="Legs"||(m.deployed&&m.deployment>=.99999f)),"collider/ladder gate");}if(m.deploymentID=="Stairs"){bool open=m.deployed&&m.deployment>=.99999f;Check(m.part.hatch.enabled==open,"boarding trigger gate");Check((m.part.airlock!=null)==open,"cached exit gate");if(HighLogic.LoadedSceneIsFlight)Check(m.part.noAutoEVAAny==!open,"portrait EVA gate");}}
 public static void Run(string id,ConfigNode cfg){
  HighLogic.LoadedSceneIsEditor=true;HighLogic.LoadedSceneIsFlight=false;var a=Setup(id,cfg,1,true);Pose(a,cfg);Check(a.status=="Lowered","initial deployed state");
  var b=Setup(id,cfg,1,true);a.part.symmetryCounterparts.Add(b.part);b.part.symmetryCounterparts.Add(a.part);
  a.Retract();Check(!a.deployed&&!b.deployed,"symmetry target");for(int i=0;i<18;i++){a.Update();Pose(a,cfg);}float halfway=a.deployment;a.Deploy();Check(a.deployment==halfway,"reverse must not teleport");for(int i=0;i<100;i++)a.Update();Pose(a,cfg);Check(a.deployment==1,"lowered endpoint");
  a.ToggleAction(new KSPActionParam());for(int i=0;i<100;i++){a.Update();b.Update();}Pose(a,cfg);Pose(b,cfg);Check(a.deployment==0&&b.deployment==0&&a.Events["Deploy"].active,"raised endpoint and control");
  var copied=Setup(id,cfg,0,false);copied.Deploy();for(int i=0;i<100;i++)copied.Update();Pose(copied,cfg);Check(copied.deployment==1,"copied retracted part recovers authoritative deployed position");
  HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;var hook=Setup(id,cfg,1,true);int before=ModuleRWGroundTether.releases;hook.Retract();Check(ModuleRWGroundTether.releases==before+(id=="Legs"?1:0),"tether release hook on legs only");Check(hook.deployment==1,"tether released before leg motion");var loaded=Setup(id,cfg,.4f,false);Pose(loaded,cfg);loaded.Update();Check(loaded.deployment==.4f,"flight doesn't advance in editor Update");for(int i=0;i<100;i++)loaded.FixedUpdate();Pose(loaded,cfg);Check(loaded.deployment==0,"flight persisted transition resumes");loaded.DeployAction(new KSPActionParam());for(int i=0;i<100;i++)loaded.FixedUpdate();Pose(loaded,cfg);Check(loaded.deployment==1,"flight action lower");
  if(id=="Stairs"){
   loaded.Retract();Check(loaded.part.noAutoEVAAny&&!loaded.part.hatch.enabled&&loaded.part.airlock==null,"EVA blocks immediately before first movement");
   loaded.part.airlock=loaded.part.hatch.transform;loaded.part.noAutoEVAAny=false;loaded.LateUpdate();Check(loaded.part.airlock==null&&loaded.part.noAutoEVAAny,"late startup binding cannot reopen a raised stair hatch");
   loaded.Deploy();for(int i=0;i<100;i++)loaded.FixedUpdate();Check(!loaded.part.noAutoEVAAny&&loaded.part.airlock!=null,"EVA restored when fully lowered");
   loaded.part.noAutoEVAAny=true;loaded.Retract();loaded.Deploy();for(int i=0;i<100;i++)loaded.FixedUpdate();Check(loaded.part.noAutoEVAAny,"pre-existing game/mod restriction retained");
   loaded.part.noAutoEVAAny=false;loaded.Retract();loaded.OnDestroy();Check(!loaded.part.noAutoEVAAny,"cleanup releases owned lock");
   var missing=Setup(id,cfg,1,true,false);Check(missing.part.noAutoEVAAny&&missing.part.airlock==null,"missing hatch fails closed");
   var restricted=Setup(id,cfg,0,false,true,true);restricted.Deploy();for(int i=0;i<100;i++)restricted.FixedUpdate();Check(restricted.part.noAutoEVAAny,"raised flight load preserves pre-existing restriction");
   foreach(bool savedFlag in new[]{false,true}){var reload=Setup(id,cfg,0,false,true,savedFlag,true,false);Check(reload.part.noAutoEVAAny&&reload.evaLockOwned,"reload reasserts owned lock");reload.Deploy();for(int i=0;i<100;i++)reload.FixedUpdate();Check(!reload.part.noAutoEVAAny&&!reload.evaLockOwned,"saved owned lock releases after lowering");}
   HighLogic.LoadedSceneIsEditor=true;HighLogic.LoadedSceneIsFlight=false;var editor=Setup(id,cfg,0,false);Check(!editor.part.noAutoEVAAny,"editor clones carry no portrait lock");
   var fromFlight=Setup(id,cfg,0,false,true,true,true,false);Check(!fromFlight.part.noAutoEVAAny&&!fromFlight.evaLockOwned,"editor clears a copied temporary flight lock");
  }
 }
}
'@
Add-Type -TypeDefinition ($source+"`n"+$doubles)
foreach($file in Get-ChildItem (Join-Path $kit 'Reports/RW_GND_*.json')){
 $report=Get-Content $file.FullName -Raw | ConvertFrom-Json
 foreach($id in @('Legs','Stairs')){
  $bindings=@($report.motion | Where-Object mechanism -eq $id)
  if($bindings.Count -eq 0){continue}
  $cfg=[ConfigNode]::new('MODULE');$cfg.AddValue('name','ModuleRWGroundDeploy');$cfg.AddValue('deploymentID',$id)
  foreach($b in $bindings){$n=[ConfigNode]::new('TRANSFORM');$n.AddValue('name',$b.name);$n.AddValue('deployPosition',($b.position -join ','));$n.AddValue('retractPosition',($b.retractPosition -join ','));$n.AddValue('retractEuler',($b.retractEuler -join ','));$cfg.AddNode($n)}
  [GroundDeployTest]::Run($id,$cfg)
  Write-Output "PASS controller logic $($report.role)/$id : endpoints, reversal, symmetry, clone, restore, collision/ladder gating, immediate portrait lock, late binding and prior restrictions"
 }
}

