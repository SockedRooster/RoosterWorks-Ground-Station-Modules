namespace UnityEngine {}
public class KSPField:Attribute {public bool isPersistant,guiActiveEditor;public string guiName;}
public class UI_ChooseOption:Attribute {public string[] options;public UI_Scene affectSymCounterparts;}
public enum UI_Scene {Editor}public enum StartState {Editor,Flight}
public class Control {public Action<BaseField,object> onFieldChanged,onSymmetryFieldChanged;}
public class BaseField {public Control uiControlEditor=new Control();}
public class PartModule {public Part part;public Dictionary<string,BaseField> Fields=new Dictionary<string,BaseField>{{"contents",new BaseField()}};public virtual void OnStart(StartState s){}public virtual string GetInfo(){return "";}}
public class ConfigNode {public Dictionary<string,string> values=new Dictionary<string,string>();public List<ConfigNode> children=new List<ConfigNode>();public string tag;public string GetValue(string n){return values.ContainsKey(n)?values[n]:null;}public ConfigNode[] GetNodes(string n){return children.FindAll(c=>c.tag==n).ToArray();}}
public class GameDatabase {public static GameDatabase Instance=new GameDatabase();public List<ConfigNode> sets=new List<ConfigNode>();public ConfigNode[] GetConfigNodes(string n){return n=="RW_LOG_LOADOUTS"?sets.ToArray():new ConfigNode[0];}}
public class PartResource {public double amount,maxAmount;}
public class ResourceList {public Dictionary<string,PartResource> all=new Dictionary<string,PartResource>();public PartResource this[string n]{get{return all.ContainsKey(n)?all[n]:null;}}public void Remove(string n){all.Remove(n);}}
public class Part {public ResourceList Resources=new ResourceList();public void AddResource(ConfigNode n){Resources.all[n.GetValue("name")]=new PartResource{amount=double.Parse(n.GetValue("amount"),CultureInfo.InvariantCulture),maxAmount=double.Parse(n.GetValue("maxAmount"),CultureInfo.InvariantCulture)};}}
public class PartResourceLibrary {public static PartResourceLibrary Instance=new PartResourceLibrary();public HashSet<string> names=new HashSet<string>();public object GetDefinition(string n){return names.Contains(n)?this:null;}}
public static class HighLogic {public static bool LoadedSceneIsEditor=true;}
public class EditorLogic {public static EditorLogic fetch=new EditorLogic();public object ship=new object();}
public class Event {public int calls;public void Fire(object o){calls++;}}
public static class GameEvents {public static Event onPartResourceListChange=new Event(),onEditorShipModified=new Event();}
public static class MonoUtilities {public static void RefreshContextWindows(Part p){}}
public static class GroundLogisticsTest {
 static int checks;static void Check(bool c,string s){checks++;if(!c)throw new Exception(s);}static void Near(double a,double b,string s){Check(Math.Abs(a-b)<1e-6,s);}
 static ConfigNode set=new ConfigNode{tag="RW_LOG_LOADOUTS",values=new Dictionary<string,string>{{"name","RW_GND_LOG"}}};
 public static void AddChoice(string name,string[] resources,double[] amounts,double[] capacities){var c=new ConfigNode{tag="LOADOUT",values=new Dictionary<string,string>{{"name",name}}};for(int i=0;i<resources.Length;i++){PartResourceLibrary.Instance.names.Add(resources[i]);c.children.Add(new ConfigNode{tag="RESOURCE",values=new Dictionary<string,string>{{"name",resources[i]},{"amount",amounts[i].ToString(CultureInfo.InvariantCulture)},{"maxAmount",capacities[i].ToString(CultureInfo.InvariantCulture)}}});}set.children.Add(c);}
 static ModuleRWGroundLogisticsContents New(){var p=new Part();p.Resources.all["ElectricCharge"]=new PartResource{amount=1234,maxAmount=2980};p.Resources.all["EnrichedUranium"]=new PartResource{amount=1.5,maxAmount=1.5};return new ModuleRWGroundLogisticsContents{part=p};}
 static void Verify(ModuleRWGroundLogisticsContents m,ConfigNode choice){Check(m.part.Resources.all.Count==choice.children.Count+2,"old loadout resources removed");foreach(var r in choice.children){var v=m.part.Resources[r.GetValue("name")];Check(v!=null,"resource present");Near(v.maxAmount,double.Parse(r.GetValue("maxAmount"),CultureInfo.InvariantCulture),"capacity");}Near(m.part.Resources["ElectricCharge"].amount,1234,"EC preserved");Near(m.part.Resources["EnrichedUranium"].amount,1.5,"reactor fuel preserved");}
 public static void Run(){GameDatabase.Instance.sets.Add(set);Check(set.children.Count==10,"ten choices including CO2/H2 and retained waste tanks");
 foreach(var initial in set.children)foreach(var next in set.children){var m=New();m.contents=initial.GetValue("name");m.OnStart(StartState.Editor);Verify(m,initial);m.contents=next.GetValue("name");m.Fields["contents"].uiControlEditor.onFieldChanged(null,null);Verify(m,next);for(int i=0;i<60;i++)m.Update();Verify(m,next);}
 var drained=New();drained.contents="Hydrogen";drained.OnStart(StartState.Editor);drained.part.Resources["Hydrogen"].amount=50;for(int i=0;i<100;i++)drained.Update();Near(drained.part.Resources["Hydrogen"].amount,50,"same choice never refills depletion");
 drained.part.Resources["Hydrogen"].maxAmount=1000;drained.part.Resources["Hydrogen"].amount=500;for(int i=0;i<30;i++)drained.Update();Near(drained.part.Resources["Hydrogen"].amount,375000,"capacity resize preserves fill fraction");
 var atomic=New();atomic.OnStart(StartState.Editor);PartResourceLibrary.Instance.names.Remove("Hydrogen");atomic.contents="Hydrogen";atomic.Update();Verify(atomic,set.children[0]);PartResourceLibrary.Instance.names.Add("Hydrogen");
 HighLogic.LoadedSceneIsEditor=false;var flight=New();flight.contents="Hydrogen";flight.OnStart(StartState.Flight);for(int i=0;i<100;i++)flight.Update();Check(flight.part.Resources.all.Count==2,"flight resources never reconciled or refilled");HighLogic.LoadedSceneIsEditor=true;
 var invalid=New();invalid.contents="missing profile";invalid.OnStart(StartState.Editor);Check(invalid.part.Resources.all.Count==2,"unknown choice preserves cargo");
 var attr=(UI_ChooseOption)Attribute.GetCustomAttribute(typeof(ModuleRWGroundLogisticsContents).GetField("contents"),typeof(UI_ChooseOption));Check(Array.IndexOf(attr.options,"Carbon Dioxide")>=0&&Array.IndexOf(attr.options,"Hydrogen")>=0,"new resources visible in selector");
 Console.WriteLine("PASS "+checks+" ground-logistics assertions: all choice pairs, mixed/dedicated capacities, CO2/H2 cleanup, editor refresh, no refill, atomic availability, flight preservation and unrelated resources");}
}
