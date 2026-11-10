"""Ground exterior pass. Run with Blender's standalone Python and NumPy; no rendering."""
from pathlib import Path
import io, json, math, os, struct, sys, zipfile
import numpy as np

here = Path(__file__).resolve().parent
sdk = next((here.parent/"Releases/2026-11-02").glob("*Modules*Source"))
sys.path[:0] = [str(sdk/"Source"), str(sdk/"Tools")]
from build_hab250 import Writer, Mesh, tube
from native_model import load
from native_derivatives import write_node
from config_nodes import parse

prefix = "GameData/RoosterWorksGroundModules/"
modeldir = prefix+"Models/"
source = next(Path("D:/Downloads/SourceArchives").glob("*Ground-Modules-v0.8.0-dev.32*zip"))
station = sdk/"GameData/RoosterWorksStationModules/Models"
scratch = here/"Build"
scratch.mkdir(exist_ok=True)
with zipfile.ZipFile(source) as z:
    files = {p:z.read(p) for p in z.namelist() if p.startswith(prefix) and not p.endswith("/")}
original = files.copy()
for key in ("cladding","cladding_white","hubblanket","steel","graphite","rail","bronze","ceramic","white","service_blue","service_yellow"):
    name = "rwm_"+key+".png"
    files[modeldir+name] = (station/name).read_bytes()

class Buffer(Writer):
    def __init__(self):
        self.handle=io.BytesIO()
    def data(self):
        return self.handle.getvalue()

def mesh_node(name,mesh,index):
    return dict(name="RW_Ground_"+name,position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),
                children=[],shadows=(1,1),materials=[index],mesh=dict(vertices=mesh.vertices,
                normals=mesh.normals,uvs=mesh.uvs,submeshes=[mesh.triangles]))

def table(data,tag,entries):
    header=Buffer()
    header.i(tag,len(entries))
    header.s(entries[0]["name"])
    assert data.count(header.data())==1
    return data.index(header.data())

def append_hardware(data,model,groups):
    # Append native records without reserializing the existing animations, materials or meshes.
    mi=table(data,10,model.materials)
    ti=table(data,12,model.textures)
    nodes,mats,tex=Buffer(),Buffer(),Buffer()
    texture_names=[entry["name"] for entry in model.textures]
    for i,(name,key,mesh) in enumerate(groups):
        texture_name="rwm_"+key
        if texture_name not in texture_names:
            texture_names.append(texture_name)
            tex.s(texture_name); tex.i(0)
        nodes.i(0)
        write_node(nodes,mesh_node(name,mesh,len(model.materials)+i))
        nodes.i(1)
        mats.s("RW_GroundDetail_"+name)
        mats.s("KSP/Specular")
        mats.i(4)
        mats.s("_MainTex"); mats.i(4,texture_names.index(texture_name)); mats.f(1,1,0,0)
        mats.s("_Color"); mats.i(0); mats.f(1,1,1,1)
        mats.s("_SpecColor"); mats.i(0); mats.f(.28,.29,.30,1)
        mats.s("_Shininess"); mats.i(2); mats.f(.24)
    return (data[:mi]+nodes.data()+struct.pack("<ii",10,len(model.materials)+len(groups))
            +data[mi+8:ti]+mats.data()+struct.pack("<ii",12,len(texture_names))
            +data[ti+8:]+tex.data())

def shell_triangles(model):
    # Root-level static skins share part coordinates; moving stairs, drill gear and legs have their own parents.
    blocks=[]
    for n in model.root["children"]:
        if "mesh" not in n or n["position"]!=(0,0,0) or n["rotation"]!=(0,0,0,1): continue
        for idx,tris in zip(n["materials"],n["mesh"]["submeshes"]):
            props=model.materials[idx]["properties"]
            if "_MainTex" not in props: continue
            texture=model.textures[props["_MainTex"]["index"]]["name"]
            if texture not in ("rwm_cladding","rwm_cladding_white","rwm_ceramic","rwm_white","rwm_hubblanket","rwm_steel","rwm_graphite","rwm_rail"): continue
            blocks.append(np.asarray(n["mesh"]["vertices"])[np.asarray(tris)])
    return np.concatenate(blocks)

def skin_sampler(tris,normal):
    # Intersect radial rays with the rendered triangle surfaces. Use axial position and
    # lateral distance from the radial plane as the two barycentric coordinates.
    tangent=np.array((0,-normal[2],normal[1]))
    x=tris[:,:,0]; y=tris@tangent; r=tris@normal
    keep=(y.min(1)<=0)&(y.max(1)>=0)
    x,y,r=x[keep],y[keep],r[keep]
    dx=x[:,1:]-x[:,:1];dy=y[:,1:]-y[:,:1]
    det=dx[:,0]*dy[:,1]-dx[:,1]*dy[:,0]
    det[np.abs(det)<1e-12]=np.nan
    def radius(pos):
        px=pos-x[:,0];py=-y[:,0]
        u=(px*dy[:,1]-py*dx[:,1])/det;v=(py*dx[:,0]-px*dy[:,0])/det
        rr=r[:,0]+u*(r[:,1]-r[:,0])+v*(r[:,2]-r[:,0])
        valid=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(rr>.7)
        if not np.any(valid): raise ValueError(("missing hull contact",pos))
        return float(rr[valid].max())
    return radius

def build(role):
    key="RW_GND_"+role
    path=scratch/(key+".mu")
    raw=files[modeldir+path.name];path.write_bytes(raw);model=load(path)
    part=parse(files[prefix+"Parts/"+key+".cfg"].decode("utf-8-sig")).children[0]
    bounds=sorted(float(part.get("node_stack_"+end).split(",")[0]) for end in ("top","bottom"))
    xs=np.linspace(*bounds,max(41,round((bounds[1]-bounds[0])/.025)))
    tris=shell_triangles(model)
    rails,blue,yellow,feet,clamps=map(lambda _:Mesh(),range(5))
    count=0
    for sign in (-1,1):
        for angle,mesh,radius,width in [(72,rails,1.315,.017),(76,blue,1.30,.009),(78,yellow,1.30,.009)]:
            a=math.radians(angle);n=np.array((0,math.sin(a),sign*math.cos(a)))
            skin=skin_sampler(tris,n)
            # All collars share these cross-section coordinates. Only the post lengths
            # follow local skin height so panel seams cannot put kinks in the tubes.
            offset=radius*n
            assert max(skin(x) for x in xs[1:-1])+width < radius, (key,angle,sign)
            tube(mesh,offset+[bounds[0],0,0],offset+[bounds[1],0,0],width,12)
            for j in np.unique(np.linspace(3,len(xs)-4,max(3,math.ceil((xs[-1]-xs[0])/.45))).astype(int)):
                x=xs[j]; foot=np.array((x,0,0))+skin(x)*n
                top=np.array((x,0,0))+offset
                if mesh is rails:
                    tube(feet,foot-.012*n,foot+.009*n,.046,12)
                    tube(clamps,foot+.004*n,top,.017,10)
                    tube(clamps,top-.029*np.array((1,0,0)),top+.029*np.array((1,0,0)),width+.003,12)
                else:
                    tube(feet,foot-.009*n,foot+.006*n,.023,10)
                    tube(clamps,foot,top,.010,8)
                    tube(clamps,top-.018*np.array((1,0,0)),top+.018*np.array((1,0,0)),width+.004,10)
                count+=1
    groups=[("Handrails","rail",rails),("BlueLoom","service_blue",blue),("YellowLoom","service_yellow",yellow),
            ("MountingFeet","graphite",feet),("CableClips","steel",clamps)]
    data=append_hardware(raw,model,groups);path.write_bytes(data)
    check=load(path)
    assert check.root["children"][:-5]==model.root["children"]
    assert check.materials[:len(model.materials)]==model.materials
    assert all(check.textures[i]["name"]+".png" in [Path(p).name for p in files] for i in range(len(model.textures),len(check.textures)))
    files[modeldir+path.name]=data
    print(key,count,"anchored fittings",flush=True)

if __name__ == '__main__':
    for role in ("HAB","CMD","LAB","TUB","LOG","PWR","AIR","ISRU","CEN","NST","NSM"):
        build(role)
    version=prefix+"RoosterWorksGroundModules.version"
    meta=json.loads(files[version]); meta["VERSION"]["BUILD"]=34
    files[version]=(json.dumps(meta,indent=2)+"\n").encode()
    target=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.34-Install.zip"
    tmp=target.with_suffix(".partial")
    with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p,data in sorted(files.items()):z.writestr(p,data)
    with zipfile.ZipFile(tmp) as z:
        assert len(z.namelist())==len(files) and all(z.read(p)==b for p,b in files.items())
    assert all(files[p]==v for p,v in original.items() if p.endswith((".cfg",".dll")))
    os.replace(tmp,target)
    print(target)
