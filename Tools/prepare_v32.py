from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];B=R.parent/'ground-hotpatch-v31';GD=R/'GameData/RoosterWorksGroundModules'
p=R/'Tools/TubeMotionDoubles.cs';s=(B/'Tools/TubeMotionDoubles.cs').read_text()
s=s.replace('public Vector3 TransformPoint(Vector3 v){return position+TransformVector(v);}', 'public Vector3 TransformPoint(Vector3 v){return position+TransformVector(v);}public Vector3 InverseTransformPoint(Vector3 v){return InverseTransformVector(v-position);}')
s=s.replace('public virtual void OnLoad(ConfigNode n){}','public virtual void OnLoad(ConfigNode n){}public virtual void OnSave(ConfigNode n){}')
s=s.replace('public uint flightID;', 'public UnityEngine.Vector3 orgPos;public void UpdateOrgPosAndRot(Part root){orgPos=root.transform.InverseTransformPoint(transform.position);}public uint flightID;')
s=s.replace('public class Vessel {public bool', 'public class Precalc {public bool isEasingGravity;}\npublic class Vessel {public Part rootPart;public Precalc precalc;public bool')
s=s.replace('public static class GameEvents {', 'public class VesselEvent {public event Action<Vessel> Handlers;public void Add(Action<Vessel> f){Handlers+=f;}public void Remove(Action<Vessel> f){Handlers-=f;}public void Fire(Vessel v){if(Handlers!=null)Handlers(v);}}\npublic static class GameEvents {public static VesselEvent onVesselGoOnRails=new VesselEvent(),onVesselGoOffRails=new VesselEvent();')
p.write_text(s)
p=R/'Tools/TubeMotionTests.cs';s=(B/'Tools/TubeMotionTests.cs').read_text().replace('m.Extend();float last=0;', 'm.FixedUpdate();float baseline=hostTube?joint.anchor.x:joint.connectedAnchor.x;m.Extend();float last=baseline;').replace('Near(last,2.8f,"full extension joint travel")','Near(last-baseline,2.8f,"full extension joint travel")')
s=s.replace('Console.WriteLine("PASS "+checks', '''HighLogic.LoadedSceneIsEditor=false;HighLogic.LoadedSceneIsFlight=true;
 foreach(float selected in new[]{.137f,.5f,1f}){
  var m=Tube(selected);var f=Attach(m);var v=m.vessel;v.rootPart=m.part;v.parts.Add(m.part);v.parts.Add(f);var tail=new Part{vessel=v};tail.transform.position=new UnityEngine.Vector3(8f,1,2);v.parts.Add(tail);
  float before=f.transform.position.x;var other=Tube(.1f);float otherPose=other.extension;
  for(int cycle=0;cycle<12;cycle++){
   GameEvents.onVesselGoOnRails.Fire(v);Near(f.orgPos.x,before,"rails snapshots extended payload");Near(tail.orgPos.x,8,"rails snapshots entire assembly");
   v.packed=true;TimeWarp.CurrentRateIndex=5;f.transform.position=m.part.transform.TransformPoint(f.orgPos);tail.transform.position=m.part.transform.TransformPoint(tail.orgPos);
   m.part.transforms["RW_TubeBellows"].localScale=new UnityEngine.Vector3(1,1,1);m.LateUpdate();Tick(m,5);Pose(m,selected);Near(f.transform.position.x,before,"no packed collapse");
   v.packed=false;TimeWarp.CurrentRateIndex=0;f.attachJoint=new PartJoint();var j=new UnityEngine.ConfigurableJoint{host=f.Rigidbody,connectedBody=m.part.Rigidbody};f.attachJoint.joints.Add(j);
   GameEvents.onVesselGoOffRails.Fire(v);Near(f.transform.TransformPoint(j.anchor).x,m.part.transform.TransformPoint(j.connectedAnchor).x,"rebuilt joint zero preload");Tick(m,2);Near(f.transform.position.x,before,"no unpack jump");Pose(m,selected);Near(other.extension,otherPose,"unrelated vessel preserved");
  }
  m.OnSave(new ConfigNode());Near(f.orgPos.x,before,"save keeps extended assembly");m.OnDestroy();other.OnDestroy();
 }
 Console.WriteLine("PASS "+checks''')
at=s.index('foreach(float selected in new[]{.137f,.5f,1f})')
import re
s=s[:at]+re.sub(r'\bf\b','warpFront',s[at:])
p.write_text(s)
v=GD/'RoosterWorksGroundModules.version';data=json.loads(v.read_text());data['VERSION']['BUILD']=32;v.write_text(json.dumps(data,indent=2)+'\n')
cmd=GD/'Parts/RW_GND_CMD.cfg';s=(B/'GameData/RoosterWorksGroundModules/Parts/RW_GND_CMD.cfg').read_text();i=s.rfind('}');s=s[:i]+'    MODULE\n    {\n        name = ModuleRWGroundLevel\n    }\n'+s[i:];cmd.write_text(s)
protected={p.relative_to(B).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'GameData').rglob('*') if p.is_file()}
(R/'Reports/DEV32_BASELINE.json').write_text(json.dumps(protected,indent=2)+'\n')
print('PASS prepared dev.32 configuration and warp lifecycle tests')
