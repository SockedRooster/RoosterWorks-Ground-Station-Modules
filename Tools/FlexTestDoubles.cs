namespace UnityEngine {
 public struct Vector3 {public float x,y,z;public Vector3(float a,float b,float c){x=a;y=b;z=c;}}
 public class Transform {public Vector3 localPosition;public Vector3 localScale=new Vector3(1,1,1);}
 public static class Time {public static float deltaTime=.02f,fixedDeltaTime=.02f;}
 public static class Mathf {public static float Max(float a,float b){return Math.Max(a,b);}public static float Clamp01(float a){return Math.Max(0,Math.Min(1,a));}public static float MoveTowards(float a,float b,float step){return Math.Abs(a-b)<=step?b:a+Math.Sign(b-a)*step;}}
 public struct Color {public float r,g,b,a;public Color(float x,float y,float z,float w){r=x;g=y;b=z;a=w;}}
 public class MaterialPropertyBlock {public Color color;public int other;public void SetColor(string name,Color value){if(name!="_EmissiveColor")throw new Exception("wrong shader property");color=value;}}
 public class Renderer {public string name;public Color color;public int other=123;public void GetPropertyBlock(MaterialPropertyBlock b){b.color=color;b.other=other;}public void SetPropertyBlock(MaterialPropertyBlock b){color=b.color;other=b.other;}}
}
public class KSPField:Attribute {public bool isPersistant,guiActive,guiActiveEditor;public string guiName;}
public class KSPEvent:Attribute {public bool guiActive,guiActiveEditor;public string guiName;}
public class KSPAction:Attribute {public KSPAction(string name){}}
public class KSPActionParam {}
public class ConfigNode {}
public enum StartState {None}
public class Control {public bool active,guiActive,guiActiveEditor;}
public class EventList:System.Collections.Generic.Dictionary<string,Control>{public bool Contains(string n){return ContainsKey(n);}}
public class PartModule {public Part part;public Vessel vessel{get{return part==null?null:part.vessel;}}public EventList Events=new EventList{{"Extend",new Control()},{"Collapse",new Control()}};public virtual void OnLoad(ConfigNode n){}public virtual void OnStart(StartState s){}public virtual void OnStartFinished(StartState s){}public virtual string GetInfo(){return "";}}
public class ModuleDockingNode:PartModule {public string referenceAttachNode,state="Ready";public uint dockedPartUId;public ModuleDockingNode otherNode;}
public class ModuleLight:PartModule {public string lightName;public bool isOn;}
public class AttachNode {public Part attachedPart;public UnityEngine.Vector3 position,originalPosition;}
public class Vessel {public bool loaded=true,packed;}
public class Part {public Vessel vessel=new Vessel();public System.Collections.Generic.Dictionary<string,UnityEngine.Transform> transforms=new System.Collections.Generic.Dictionary<string,UnityEngine.Transform>();public System.Collections.Generic.Dictionary<string,AttachNode> nodes=new System.Collections.Generic.Dictionary<string,AttachNode>();public System.Collections.Generic.List<PartModule> modules=new System.Collections.Generic.List<PartModule>();public System.Collections.Generic.List<UnityEngine.Renderer> renderers=new System.Collections.Generic.List<UnityEngine.Renderer>();public UnityEngine.Transform FindModelTransform(string n){return transforms.ContainsKey(n)?transforms[n]:null;}public AttachNode FindAttachNode(string n){return nodes.ContainsKey(n)?nodes[n]:null;}public System.Collections.Generic.List<T> FindModulesImplementing<T>(){var result=new System.Collections.Generic.List<T>();foreach(var m in modules)if(m is T)result.Add((T)(object)m);return result;}public System.Collections.Generic.List<T> FindModelComponents<T>(string name){var result=new System.Collections.Generic.List<T>();foreach(var r in renderers)if(r.name==name)result.Add((T)(object)r);return result;}}
public static class HighLogic {public static bool LoadedSceneIsFlight=true,LoadedSceneIsEditor;}
public static class TimeWarp {public static int CurrentRateIndex;}
public class EditorLogic {public static EditorLogic fetch;public object ship=new object();}
public class EditorEvent {public int calls;public void Fire(object o){calls++;}}
public static class GameEvents {public static EditorEvent onEditorShipModified=new EditorEvent();}
