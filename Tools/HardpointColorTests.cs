public static class HardpointColorTest {
 static int checks;static void Check(bool c,string s){checks++;if(!c)throw new Exception(s);}
 static List<UnityEngine.Renderer> renderers=new List<UnityEngine.Renderer>();
 static List<UnityEngine.Mesh> native=new List<UnityEngine.Mesh>();
 static List<int[]> expectedRings=new List<int[]>(),expectedBodies=new List<int[]>();
 static bool Equal(int[] a,int[] b){if(a.Length!=b.Length)return false;for(int i=0;i<a.Length;i++)if(a[i]!=b[i])return false;return true;}
 static ConfigNode map=new ConfigNode("RW_RING_MAP");
 public static void Add(string path,string texture,int vertexCount,int[] triangles,string ranges){
  var spec=new ConfigNode("MESH");spec.AddValue("path",path);spec.AddValue("texture",texture);spec.AddValue("vertices",vertexCount);spec.AddValue("triangles",triangles.Length/3);spec.AddValue("ranges",ranges);map.nodes.Add(spec);
  UnityEngine.Transform transform=null;foreach(string segment in path.Trim('/').Split('/'))transform=new UnityEngine.Transform{name=segment,parent=transform};
  var mesh=new UnityEngine.Mesh{vertexCount=vertexCount};mesh.sub[0]=triangles;native.Add(mesh);
  var selected=new bool[triangles.Length/3];foreach(string range in ranges.Split(',')){var pair=range.Split(':');int start=int.Parse(pair[0]),count=int.Parse(pair[1]);for(int i=start;i<start+count;i++)selected[i]=true;}
  var rings=new List<int>();var body=new List<int>();for(int i=0;i<selected.Length;i++){var dst=selected[i]?rings:body;for(int k=0;k<3;k++)dst.Add(triangles[i*3+k]);}expectedRings.Add(rings.ToArray());expectedBodies.Add(body.ToArray());
  renderers.Add(new UnityEngine.Renderer{transform=transform,filter=new UnityEngine.MeshFilter{sharedMesh=mesh},materials=new[]{new UnityEngine.Material{name="native",mainTexture=new UnityEngine.Texture(texture)}}});
  foreach(string color in new[]{"steel","white","charcoal","blue","green","red","gold"})GameDatabase.Instance.textures["RoosterWorksStationModules/Models/rwm_ring_"+texture+"_"+color]=new UnityEngine.Texture(color);
 }
 public static void Run(){
  map.AddValue("model","RW_GND_HPT");GameDatabase.Instance.nodes.Add(map);var part=new Part{renderers=renderers.ToArray()};
  // Reproduce the exact dev.7 failure with the shipped runtime and real mesh.
  string good=map.nodes[0].GetValue("ranges");map.nodes[0].AddValue("ranges","0-255");
  var broken=new ModuleRWRingColor{part=part,ringModel="RW_GND_HPT",ringColor="Blue"};bool failed=false;
  try{broken.OnStart(StartState.None);}catch(FormatException){failed=true;}
  Check(failed,"old hyphen map reproduces reported FormatException");map.nodes[0].AddValue("ranges",good);
  var controller=new ModuleRWRingColor{part=part,ringModel="RW_GND_HPT",ringColor="Original"};controller.OnStart(StartState.None);
  foreach(string color in new[]{"Steel","White","Charcoal","Blue","Green","Red","Gold","Original"}){
   controller.ringColor=color;controller.Fields["ringColor"].uiControlEditor.onFieldChanged(controller.Fields["ringColor"],"");
   for(int cycle=0;cycle<40;cycle++){
    for(int i=0;i<35;i++)controller.Update();
    for(int j=0;j<renderers.Count;j++){
     var r=renderers[j];Check(r.filter.sharedMesh.subMeshCount==2,"ring partition");Check(Equal(r.filter.sharedMesh.GetTriangles(1),expectedRings[j]),"exact selected ring triangles retained");Check(Equal(r.filter.sharedMesh.GetTriangles(0),expectedBodies[j]),"exact unmapped body triangles retained");
     if(color!="Original")Check(r.materials[1].mainTexture.name==color.ToLowerInvariant(),"color applies after repeated menu polling");
    }
   }
  }
  // A reopened menu/model reset is rebound using the same actual config.
  controller.ringColor="Green";for(int j=0;j<renderers.Count;j++){renderers[j].filter.sharedMesh=native[j].Clone();renderers[j].materials=new[]{new UnityEngine.Material{name="rebuilt",mainTexture=new UnityEngine.Texture("white")}};}
  for(int i=0;i<35;i++)controller.Update();foreach(var r in renderers)Check(r.materials[1].mainTexture.name=="green","native reset rebinding");
  Check(UnityEngine.Debug.errors==0,"no map/texture errors");controller.OnDestroy();foreach(var r in renderers)Check(r.materials.Length==1,"ownership cleanup");
  Console.WriteLine("PASS "+checks+" actual-map color assertions: old FormatException reproduced; real colon-count maps; all colors; repeated polling/reopen/reset; no new errors");
 }
}
