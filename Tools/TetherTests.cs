public static class TetherTest
{
    static int checks; static uint nextID=1;
    static void Check(bool value,string text){checks++;if(!value)throw new Exception(text);}
    static object Field(object m,string name){return m.GetType().GetField(name,System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.Instance).GetValue(m);}
    static System.Collections.IList Anchors(ModuleRWGroundTether m){return (System.Collections.IList)Field(m,"anchors");}
    static Part AddPart(Vessel v,string name){var p=new Part{vessel=v,partInfo=new PartInfo{name=name},flightID=nextID++};var go=new UnityEngine.GameObject(name??"unnamed");p.Rigidbody=go.AddComponent<UnityEngine.Rigidbody>();p.Rigidbody.worldCenterOfMass=new UnityEngine.Vector3(v.parts.Count*4,8,v.parts.Count*.3f);p.Rigidbody.rotation=new UnityEngine.Quaternion{angle=v.parts.Count*7};v.parts.Add(p);return p;}
    static ModuleRWGroundTether Setup(Vessel v=null,bool requested=false){v=v??new Vessel();var p=AddPart(v,"RW.GND.CMD");var m=new ModuleRWGroundTether{part=p,tetherEnabled=requested};v.modules.Add(m);m.OnStart(StartState.None);return m;}
    static ModuleRWGroundTether FullBase(bool saved=false){var m=Setup(null,saved);foreach(string role in new[]{"HAB","LAB","LOG","GRN","HUB","ELB","TUB","PWR","AIR","END_250_125"})AddPart(m.vessel,"RW.GND."+role.Replace("_","."));return m;}
    static void Tick(ModuleRWGroundTether m,int count=90){for(int i=0;i<count;i++)m.FixedUpdate();}
    static void Held(ModuleRWGroundTether m,int modules,int bodies=-1){if(bodies<0)bodies=modules;Check(Anchors(m).Count==bodies,"all ground rigidbodies must be anchored: "+Anchors(m).Count+" / "+bodies);Check(m.tetherStatus=="Engaged: "+modules+"/"+modules+" modules","coverage status");var seen=new HashSet<UnityEngine.Rigidbody>();foreach(object a in Anchors(m)){var p=(Part)Field(a,"part");var rb=(UnityEngine.Rigidbody)Field(a,"body");var proxy=(UnityEngine.Rigidbody)Field(a,"proxy");var joint=(UnityEngine.FixedJoint)Field(a,"joint");Check((p.partInfo.name.StartsWith("RW_GND_")||p.partInfo.name.StartsWith("RW.GND."))&&p.vessel==m.vessel,"only connected RoosterWorks modules");Check(seen.Add(rb),"no duplicate anchor on shared body");Check(joint.connectedBody==proxy&&proxy.isKinematic&&!proxy.useGravity,"independent kinematic anchor");Check(!joint.enableCollision&&!joint.enablePreprocessing,"constraint policy");Check(joint.breakForce>=1000&&!float.IsInfinity(joint.breakForce)&&joint.breakTorque>=3000,"finite strengthened per-body limits");}}
    static List<UnityEngine.Object> Owned(ModuleRWGroundTether m){var result=new List<UnityEngine.Object>();foreach(object a in Anchors(m)){result.Add((UnityEngine.Object)Field(a,"joint"));result.Add((UnityEngine.Object)Field(a,"owner"));}return result;}
    static void Destroyed(List<UnityEngine.Object> objects){foreach(var o in objects)Check(o.destroyed,"owned physics object leaked");}
    static void Cleanup(ModuleRWGroundTether m){var objects=Owned(m);m.OnDestroy();Check(Anchors(m).Count==0,"destroy clears anchors");Destroyed(objects);}
    static void Break(ModuleRWGroundTether m){UnityEngine.Object.Destroy((UnityEngine.FixedJoint)Field(Anchors(m)[0],"joint"));m.FixedUpdate();}
    public static void Run()
    {
        // Both KSP-normalized and raw config identifiers work in one assembly.
        var mixed=FullBase();AddPart(mixed.vessel,"RW_GND_HAB");
        foreach(string name in new[]{"RW.GNDX.HAB","RW_GNDX_HAB","RW.GND","RW_GND","stockPart"})AddPart(mixed.vessel,name);
        AddPart(mixed.vessel,null);var unknown=AddPart(mixed.vessel,"unknown");unknown.partInfo=null;
        mixed.EnableTether();Tick(mixed);Held(mixed,12);Cleanup(mixed);
        var m=FullBase();AddPart(m.vessel,"stockDockingPort");Tick(m);Check(Anchors(m).Count==0&&!m.tetherEnabled,"default off");m.EnableTether();Tick(m,5);Check(Anchors(m).Count==0,"initial settle delay");Tick(m);Held(m,11);
        // Celestial surface-frame rotation must work even when the visual
        // planet Transform points elsewhere. Actual physics is not simulated.
        var a0=Anchors(m)[0];var rb0=(UnityEngine.Rigidbody)Field(a0,"body");var p0=rb0.worldCenterOfMass;float originalAngle=rb0.rotation.angle;var proxy0=(UnityEngine.Rigidbody)Field(a0,"proxy");m.vessel.mainBody.surfaceYaw=.2;m.vessel.mainBody.shift=100;m.vessel.mainBody.transform.rotation=new UnityEngine.Quaternion{angle=333};m.FixedUpdate();Check(Math.Abs(proxy0.lastRotation.angle-originalAngle-(float)(.2*180/Math.PI))<.002,"orientation uses celestial surface frame, not rendered Transform");Check(Math.Abs(proxy0.lastPosition.x-(p0.x*Math.Cos(.2)+p0.z*Math.Sin(.2)+100))<.001,"surface position tracking");Check(rb0.worldCenterOfMass.x==p0.x&&rb0.worldCenterOfMass.y==p0.y,"never teleport actual module");
        var strength=(UnityEngine.FixedJoint)Field(a0,"joint");float beforeForce=strength.breakForce;rb0.mass=80;m.FixedUpdate();Check(strength.breakForce>beforeForce,"limits adapt to resource/mass changes");
        var owned=Owned(m);m.DisableTether();Destroyed(owned);Check(Anchors(m).Count==0&&!m.tetherEnabled,"release all modules");Tick(m);Check(Anchors(m).Count==0,"off stays off");Cleanup(m);
        foreach(string reason in new[]{"airborne","water","fast","movinglegs","nolegs","throttle","wheel","kinematic","nullrb"})
        {
            var x=FullBase();if(reason=="airborne")x.vessel.Landed=false;if(reason=="water")x.vessel.Splashed=true;if(reason=="fast")x.vessel.srf_velocity=new Vector3d(2,0,0);if(reason=="movinglegs")x.vessel.supports[0].deployment=.8f;if(reason=="nolegs")x.vessel.supports.Clear();if(reason=="throttle")x.vessel.ctrlState.mainThrottle=.2f;if(reason=="wheel")x.vessel.ctrlState.wheelThrottle=-.2f;if(reason=="kinematic")x.vessel.parts[5].Rigidbody.isKinematic=true;if(reason=="nullrb")x.vessel.parts[5].Rigidbody=null;x.EnableTether();Tick(x);Check(Anchors(x).Count==0,"no partial/unsafe engagement: "+reason);Cleanup(x);
        }
        m=FullBase();m.EnableTether();m.vessel.srf_velocity=new Vector3d(.2,0,0);Tick(m);Check(Anchors(m).Count==0&&m.tetherEnabled,"wait for low engagement speed");m.vessel.srf_velocity=new Vector3d();Tick(m);Held(m,11);
        owned=Owned(m);m.vessel.precalc.isEasingGravity=true;m.FixedUpdate();Destroyed(owned);Check(Anchors(m).Count==0&&m.tetherEnabled,"gravity easing suspends every anchor");m.vessel.precalc.isEasingGravity=false;Tick(m);Held(m,11);
        owned=Owned(m);m.vessel.parts[7].Rigidbody.isKinematic=true;m.FixedUpdate();Destroyed(owned);Check(Anchors(m).Count==0&&m.tetherEnabled,"another module becoming kinematic suspends all");m.vessel.parts[7].Rigidbody.isKinematic=false;Tick(m);Held(m,11);
        owned=Owned(m);m.vessel.ctrlState.mainThrottle=1;m.FixedUpdate();Destroyed(owned);Check(!m.tetherEnabled&&Anchors(m).Count==0,"launch releases whole base");m.vessel.ctrlState.mainThrottle=0;
        m.EnableTether();Tick(m);owned=Owned(m);m.vessel.supports[0].deployed=false;m.FixedUpdate();Destroyed(owned);Check(!m.tetherEnabled,"leg movement fallback disarms all");m.vessel.supports[0].deployed=true;
        m.EnableTether();Tick(m);owned=Owned(m);ModuleRWGroundTether.ReleaseForVessel(m.vessel,"Released for leg movement");Destroyed(owned);Check(!m.tetherEnabled,"pre-motion hook releases whole base immediately");
        m.EnableTether();Tick(m);owned=Owned(m);TimeWarp.CurrentRateIndex=1;m.FixedUpdate();Destroyed(owned);Check(Anchors(m).Count==0&&m.tetherEnabled,"warp remembers requested state");TimeWarp.CurrentRateIndex=0;Tick(m);Held(m,11);
        owned=Owned(m);GameEvents.onVesselGoOnRails.Fire(m.vessel);Destroyed(owned);m.vessel.packed=true;Tick(m);Check(Anchors(m).Count==0,"packed has no anchors");m.vessel.packed=false;Tick(m);Held(m,11);
        owned=Owned(m);GameEvents.onFloatingOriginShift.Fire(new Vector3d(),new Vector3d());Destroyed(owned);Check(Anchors(m).Count==0&&m.tetherEnabled,"origin shift releases all");Tick(m);Held(m,11);
        owned=Owned(m);AddPart(m.vessel,"RW_GND_HAB");m.FixedUpdate();Destroyed(owned);Check(Anchors(m).Count==0&&m.tetherEnabled,"docking/assembly addition resets");Tick(m);Held(m,12);
        var detached=m.vessel.parts[4];owned=Owned(m);m.vessel.parts.Remove(detached);detached.vessel=new Vessel();m.FixedUpdate();Destroyed(owned);Tick(m);Held(m,11);foreach(object a in Anchors(m))Check(!ReferenceEquals(Field(a,"part"),detached),"undocked module excluded");
        // A newly joined command station inherits the connected base's switch.
        var second=Setup(m.vessel);Check(!second.tetherEnabled,"new command begins off");m.FixedUpdate();Check(second.tetherEnabled,"joined command inherits base request");Tick(m);Tick(second);Held(m,12);Check(Anchors(second).Count==0,"only elected controller creates per-part anchors");second.DisableTether();Check(!m.tetherEnabled&&!second.tetherEnabled&&Anchors(m).Count==0,"either command releases every anchor");
        m.EnableTether();Tick(m);for(int attempt=1;attempt<=3;attempt++){owned=Owned(m);Break(m);Destroyed(owned);Check(m.tetherEnabled&&second.tetherEnabled&&Anchors(m).Count==0,"transient break keeps requested state");Check(m.tetherStatus.Contains("Recovering"),"recovery status shown");Tick(m);Held(m,12);}Break(m);Check(!m.tetherEnabled&&!second.tetherEnabled&&Anchors(m).Count==0,"four repeated failures release rather than endless recovery");
        m.EnableTether();Tick(m);Break(m);Tick(m);Tick(m,800);Check((int)Field(m,"recoveryAttempts")==0,"stable hold resets recovery budget");
        m.vessel.Landed=false;owned=Owned(m);m.FixedUpdate();Destroyed(owned);Check(!m.tetherEnabled,"loss of ground releases entire base");Cleanup(second);Cleanup(m);
        var saved=FullBase(true);Tick(saved,5);Check(Anchors(saved).Count==0,"saved enabled state still settles first");Tick(saved);Held(saved,11);Cleanup(saved);
        var shared=FullBase();shared.vessel.parts[3].Rigidbody=shared.vessel.parts[2].Rigidbody;shared.EnableTether();Tick(shared);Held(shared,11,10);Cleanup(shared);
        var fail=FullBase();UnityEngine.GameObject.failAfter=UnityEngine.GameObject.jointsCreated+2;fail.EnableTether();Tick(fail);Check(!fail.tetherEnabled&&Anchors(fail).Count==0,"partial allocation failure cleans up and disarms");Check(UnityEngine.Debug.lastError.Contains("injected"),"allocation failure recorded");foreach(var go in UnityEngine.GameObject.created)if(go.name.StartsWith("RW Ground Tether /"))Check(go.destroyed,"no orphan kinematic proxy after cleanup");UnityEngine.GameObject.failAfter=0;Cleanup(fail);
        Check(GameEvents.onVesselGoOnRails.calls.Count==0&&GameEvents.onFloatingOriginShift.calls.Count==0,"all event subscriptions removed");
        var attr=(KSPField)typeof(ModuleRWGroundTether).GetField("tetherEnabled").GetCustomAttributes(typeof(KSPField),false)[0];Check(attr.isPersistant,"original saved-state field retained");
        Console.WriteLine("PASS "+checks+" distributed tether assertions: all 11 module types, per-body ownership/strength, shared bodies, joined/undocked modules, multiple commands, celestial-frame rotation, bounded recovery, pause/warp/origin/load and cleanup");
    }
}
