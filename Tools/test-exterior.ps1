$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/ExteriorLight.cs') -Raw
$test=@'
public enum StartState {Editor, Flight}
public class BasePAWGroup {public string name;public BasePAWGroup(string n,string label,bool closed){name=n;}}
public class BaseEvent {public string name,guiName;public BasePAWGroup group;public bool active=true;}
public class BaseField {public string name;public BasePAWGroup group;}
public class BaseAction {public string name,guiName;public bool active=true;}
public class BaseEventList:System.Collections.Generic.List<BaseEvent> {public bool Contains(string n){return Find(x=>x.name==n)!=null;}public BaseEvent this[string n]{get{return Find(x=>x.name==n);}}}
public class ModuleLight {
 public int starts,finished;public bool isOn,useResources=true;public float resourceAmount=.03f;
 public BaseEventList Events=new BaseEventList();public System.Collections.Generic.List<BaseField> Fields=new System.Collections.Generic.List<BaseField>();public System.Collections.Generic.List<BaseAction> Actions=new System.Collections.Generic.List<BaseAction>();
 public virtual void OnStart(StartState s){starts++;}public virtual void OnStartFinished(StartState s){finished++;}
}
public static class ExteriorTest {
 static int assertions;static void Check(bool value,string message){assertions++;if(!value)throw new System.Exception(message);}
 public static void Run(){
 foreach(StartState state in new[]{StartState.Editor,StartState.Flight})foreach(bool initial in new[]{false,true}){
 var light=new ModuleRWExteriorLight{isOn=initial};foreach(string n in new[]{"LightsOn","LightsOff","ToggleLights"})light.Events.Add(new BaseEvent{name=n});light.Fields.Add(new BaseField{name="isOn"});foreach(string n in new[]{"ToggleLightAction","LightOnAction","LightOffAction"})light.Actions.Add(new BaseAction{name=n});
 light.OnStart(state);light.OnStartFinished(state);Check(light.starts==1&&light.finished==1,"Stock lifecycle must run");Check(light.isOn==initial,"Saved state changed");Check(light.useResources&&light.resourceAmount==.03f,"Power settings changed");
 foreach(var e in light.Events){Check(e.guiName.Contains("Exterior"),"Ambiguous event name");Check(e.group.name=="RWLighting","Lost lighting group");Check(e.active,"Stock event disabled");}
 foreach(var a in light.Actions){Check(a.guiName.Contains("Exterior"),"Ambiguous action name");Check(a.active,"Stock light action disabled");}Check(light.Fields[0].group.name=="RWLighting","Ungrouped power controls");
 }
 // Missing optional events/actions must not stop stock initialization.
 var sparse=new ModuleRWExteriorLight();sparse.OnStart(StartState.Flight);sparse.OnStartFinished(StartState.Flight);Check(sparse.starts==1&&sparse.finished==1,"Sparse stock API failed");
 System.Console.WriteLine("PASS "+assertions+" exterior-light lifecycle/menu assertions");}
}
'@
Add-Type -TypeDefinition ($source+"`n"+$test)
[ExteriorTest]::Run()
