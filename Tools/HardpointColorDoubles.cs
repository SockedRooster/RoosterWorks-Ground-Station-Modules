namespace UnityEngine {
 public class Object { public static Object Instantiate(Object x) {return ((Mesh)x).Clone();} public static void Destroy(Object x) {} }
 public class Texture {public string name;public Texture(string n){name=n;}}
 public struct Color {public static Color white = new Color();}
 public class Material : Object {public string name;public Texture mainTexture;public Color color;public Material(Material x){name=x.name;CopyPropertiesFromMaterial(x);}public Material(){}public void CopyPropertiesFromMaterial(Material x){mainTexture=x.mainTexture;color=x.color;}}
 public class Transform {public string name;public Transform parent;}
 public class Mesh : Object {public string name="native";public int vertexCount=6,subMeshCount=1;public double[] vertices={0,1,2,3,4,5},uvs={.1,.2,.3},normals={1,0,0};public Dictionary<int,int[]> sub=new Dictionary<int,int[]>{{0,new[]{0,1,2,3,4,5}}};public int[] GetTriangles(int i){return sub[i];}public void SetTriangles(int[] t,int i){sub[i]=t;}public Mesh Clone(){var m=new Mesh{vertexCount=vertexCount,subMeshCount=subMeshCount,name=name,vertices=(double[])vertices.Clone(),uvs=(double[])uvs.Clone(),normals=(double[])normals.Clone()};m.sub=new Dictionary<int,int[]>();foreach(var kv in sub)m.sub[kv.Key]=(int[])kv.Value.Clone();return m;}}
 public class MeshFilter {public Mesh sharedMesh;}
 public class Renderer {public Material[] materials;public Transform transform;public MeshFilter filter;public T GetComponent<T>(){return (T)(object)filter;}}
 public static class Debug {public static int errors;public static void LogError(string x){errors++;}public static void Log(string x){}}
}
public enum UI_Scene {Editor,Flight,All}
public enum StartState {None}
public sealed class KSPField : Attribute {public bool isPersistant,guiActiveEditor;public string guiName;}
public sealed class UI_ChooseOption : Attribute {public string[] options;public UI_Scene affectSymCounterparts;}
public static class HighLogic {public static bool LoadedSceneIsEditor=true,LoadedSceneIsFlight;}
public class BaseField {public UI_Control uiControlEditor=new UI_Control();}
public class UI_Control {public Action<BaseField,object> onFieldChanged,onSymmetryFieldChanged;}
public class PartModule {public Part part;public Dictionary<string,BaseField> Fields=new Dictionary<string,BaseField>{{"ringColor",new BaseField()},{"contents",new BaseField()}};public virtual void OnStart(StartState s){}public virtual string GetInfo(){return "";}}
public class ConfigNode {public string name;public Dictionary<string,string> values=new Dictionary<string,string>();public List<ConfigNode> nodes=new List<ConfigNode>();public ConfigNode(string n){name=n;}public void AddValue(string k,object v){values[k]=Convert.ToString(v,CultureInfo.InvariantCulture);}public string GetValue(string k){return values.ContainsKey(k)?values[k]:null;}public ConfigNode[] GetNodes(string n){return nodes.FindAll(x=>x.name==n).ToArray();}}
public class GameDatabase {public static GameDatabase Instance=new GameDatabase();public Dictionary<string,UnityEngine.Texture> textures=new Dictionary<string,UnityEngine.Texture>();public List<ConfigNode> nodes=new List<ConfigNode>();public UnityEngine.Texture GetTexture(string p,bool normal){return textures.ContainsKey(p)?textures[p]:null;}public ConfigNode[] GetConfigNodes(string n){return nodes.FindAll(x=>x.name==n).ToArray();}}
public class PartResource {public double amount,maxAmount;}
public class ResourceList {public Dictionary<string,PartResource> data=new Dictionary<string,PartResource>();public PartResource this[string n]{get{return data.ContainsKey(n)?data[n]:null;}}public void Remove(string n){data.Remove(n);}}
public class PartResourceLibrary {public static PartResourceLibrary Instance=new PartResourceLibrary();public HashSet<string> definitions=new HashSet<string>{"Food","Water","Oxygen","Nitrogen","Ammonia","Waste","WasteWater"};public object GetDefinition(string n){return definitions.Contains(n)?this:null;}}
public class Part {public ResourceList Resources=new ResourceList();public UnityEngine.Renderer[] renderers=new UnityEngine.Renderer[0];public object collider=new object();public List<T> FindModelComponents<T>(){var result=new List<T>();foreach(var r in renderers)result.Add((T)(object)r);return result;}public void AddResource(ConfigNode n){Resources.data[n.GetValue("name")]=new PartResource{amount=double.Parse(n.GetValue("amount"),CultureInfo.InvariantCulture),maxAmount=double.Parse(n.GetValue("maxAmount"),CultureInfo.InvariantCulture)};}}
public class Event {public int calls;public void Fire(object p){calls++;}}
public static class GameEvents {public static Event onPartResourceListChange=new Event(),onEditorShipModified=new Event();}
public class EditorLogic {public static EditorLogic fetch=new EditorLogic();public object ship=new object();}
public static class MonoUtilities {public static int refreshes;public static void RefreshContextWindows(object p){refreshes++;}}
