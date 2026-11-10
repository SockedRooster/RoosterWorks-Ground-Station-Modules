namespace UnityEngine {public class DockTestNamespace {}}
public enum StartState {None}
public class ConfigNode {}
public enum KSPActionGroup {None=0,Custom01=1,Stage=2}
public class BaseEvent {public string name,guiName;public bool active=true,guiActive=true,guiActiveEditor=true,guiActiveUnfocused=true;}
public class BaseEventList:System.Collections.Generic.List<BaseEvent> {}
public class BaseAction {public string name;public bool active=true;public KSPActionGroup actionGroup=KSPActionGroup.Custom01;}
public class BaseActionList:System.Collections.Generic.List<BaseAction> {}
public class BaseField {public string name;public bool guiActive=true,guiActiveEditor=true;}
public class BaseFieldList:System.Collections.Generic.List<BaseField> {}
public class PartModule {public Part part;public BaseEventList Events=new BaseEventList();public BaseActionList Actions=new BaseActionList();public BaseFieldList Fields=new BaseFieldList();public virtual void OnLoad(ConfigNode n){}public virtual void OnStart(StartState s){}public virtual void OnStartFinished(StartState s){}public virtual string GetInfo(){return "";}}
public static class HighLogic {public static bool LoadedSceneIsFlight,LoadedSceneIsEditor;}
public class ModuleCommand:PartModule {}
public class ModuleDockingNodeNamed:PartModule {}
public class ModuleHabitat:PartModule {}
public class ModuleDockingNode:PartModule {
 public bool crossfeed,stagingEnabled=true,stagingToggleEnabledEditor=true,stagingToggleEnabledFlight=true;
 public string referenceAttachNode;public int enables;public ModuleDockingNode otherNode;public uint dockedPartUId;
 public float acquireRange=.5f,acquireForce=2,acquireTorque=2,acquireForceTweak=100,acquireMinFwdDot=.7f,captureRange=.06f,captureMinFwdDot=.998f,captureMaxRvel=.3f,minDistanceToReEngage=1;
 public void EnableXFeed(){enables++;crossfeed=true;foreach(var e in Events)if(e.name.Contains("XFeed"))e.active=true;}
}
public class PartInfo {public string name,title;}
public class AttachNode {public Part attachedPart;}
public class Vessel {public System.Collections.Generic.List<Part> parts=new System.Collections.Generic.List<Part>();}
public class Part {
 public bool fuelCrossFeed,stagingOn=true;public PartInfo partInfo;public uint flightID;public Vessel vessel;
 public BaseEventList Events=new BaseEventList();public BaseActionList Actions=new BaseActionList();
 public System.Collections.Generic.List<PartModule> Modules=new System.Collections.Generic.List<PartModule>();
 public System.Collections.Generic.Dictionary<string,AttachNode> nodes=new System.Collections.Generic.Dictionary<string,AttachNode>();
 public AttachNode FindAttachNode(string key){return nodes.ContainsKey(key)?nodes[key]:null;}
 public System.Collections.Generic.List<T> FindModulesImplementing<T>(){var result=new System.Collections.Generic.List<T>();foreach(var m in Modules)if(m is T)result.Add((T)(object)m);return result;}
}
