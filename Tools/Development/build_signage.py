"""Ground dev.38 signage and roof-rail finish. Keep indexed ring geometry stable."""
from build_exterior import (here,scratch,modeldir,prefix,sdk,load,np,Buffer,struct,zipfile,json,os,sys,Mesh,mesh_node,table)
from native_model import walk
from native_derivatives import write_node
from config_nodes import parse
sys.path.insert(0,str(sdk/".build-deps"))
from build_ring_options import components
from PIL import Image
import io
from pathlib import Path

base=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.37-Install.zip"
with zipfile.ZipFile(base) as z: payload={n:z.read(n) for n in z.namelist()}
keep={"PWR","LOG","CEN","NST","NSM"}
# Group only connected geometry on each old decal and look for its slightly
# larger metal surround on that same area of hull.
def bounds(points):
    return np.stack((points.min(0),points.max(0)))
def close_frame(box,target):
    return np.max(abs(box-target))<.078 and np.max(abs(box.mean(0)-target.mean(0)))<.05

docks=hatches=0
for key in sorted(n for n in payload if n.endswith(".mu")):
    path=scratch/Path(key).name; raw=payload[key]; path.write_bytes(raw); m=load(path)
    role=path.stem.removeprefix("RW_GND_")
    part=parse(payload[prefix+"Parts/"+path.stem+".cfg"].decode("utf-8-sig")).children[0]
    nodes=list(walk(m.root))
    batches=[];areas=[]; door=None;ends=0
    for address,n in nodes:
        if n.get("tag")=="Airlock":door=n["position"][0]
        if "mesh" not in n:continue
        mesh=n["mesh"];tex=m.textures[m.materials[n["materials"][0]]["properties"]["_MainTex"]["index"]]["name"]
        vs=np.array(mesh["vertices"]);tris=np.array(mesh["submeshes"][0])
        if n["name"]=="RW_EndFaceBadges":
            assert tex=="rwm_crest"
            for i in range(0,len(vs),4):
                pts=vs[i:i+4];up=pts[3]-pts[0];right=pts[1]-pts[0];normal=np.array(mesh["normals"][i])
                assert up[1]>0 and abs(up[0])+abs(up[2])<1e-5
                assert right@(-np.cross([0,1,0],normal))>0 and mesh["uvs"][i:i+4]==[(0.,0.),(1.,0.),(1.,1.),(0.,1.)]
                if role=="END_250_125" and normal[0]>.99:
                    # The large end is a structural-only attachment.
                    encoded=np.asarray(tris,dtype="<i4")
                    header=struct.pack("<ii",19,encoded.size)
                    name=Buffer();name.s(n["name"])
                    pos=raw.index(header+encoded.tobytes(),raw.index(name.data()))+8
                    pick=np.all((encoded>=i)&(encoded<i+4),axis=1)
                    assert pick.sum()==2
                    encoded[pick]=encoded[pick,0,None]
                    raw=raw[:pos]+encoded.tobytes()+raw[pos+encoded.nbytes:]
                else:ends+=1
            continue
        hide=tex=="rwm_crest" or ("label" in tex and role not in keep) or n["name"]=="RW_HPT_LabelFrame"
        batches.append((n,tex,vs,tris,hide))
        if hide and tex!="rwm_hublabel":
            for g in components(mesh):
                pts=vs[np.unique(tris[g])]
                if np.ptp(pts,axis=0).max()>.02:areas.append(bounds(pts))
    docks_in_part=sum(c.get("name")=="ModuleDockingNode" for c in part.children)
    assert ends==docks_in_part,(role,ends,docks_in_part)
    docks+=ends
    for n,tex,vs,tris,hide in batches:
        if hide:rows=np.arange(len(tris))
        elif areas and tex in ("rwm_graphite","rwm_bronze","rwm_steel"):
            rows=[i for g in components(n["mesh"]) if any(close_frame(bounds(vs[np.unique(tris[g])]),b) for b in areas) for i in g]
        else:continue
        if not len(rows): continue
        label=Buffer();label.s(n["name"])
        start=raw.index(label.data())
        encoded=np.asarray(tris,dtype="<i4");header=struct.pack("<ii",19,encoded.size)
        pos=raw.index(header+encoded.tobytes(),start)+8
        encoded[rows]=encoded[rows,0,None]
        raw=raw[:pos]+encoded.tobytes()+raw[pos+encoded.nbytes:]
    if role=="ELB":
        node=next(n for _,n in nodes if "rw_safety_yellow" in n["name"])
        # Same copper material as the straight modules' tall roof rails.
        copper=next(i for i,mat in enumerate(m.materials) if mat["name"]=="RW_GroundHardware_copper")
        label=Buffer();label.s(node["name"]);start=raw.index(label.data())
        renderer=struct.pack("<iBBii",8,*node["shadows"],1,node["materials"][0])
        pos=raw.index(renderer,start)+len(renderer)-4
        raw=raw[:pos]+struct.pack("<i",copper)+raw[pos+4:]
    if door is not None:
        # Center on the flat ivory leaf below its window. Match the outward
        # UV basis of the verified +Z docking faces.
        crest=next(i for i,mat in enumerate(m.materials) if m.textures[mat["properties"]["_MainTex"]["index"]]["name"]=="rwm_crest")
        mx=Mesh()
        pts=[(door-.085*a,-.27+.085*b,1.4465) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))]
        mx.quad(pts,[(0,0,1)]*4,reverse=True)
        rec=Buffer();rec.i(0);write_node(rec,mesh_node("HatchCrest",mx,crest));rec.i(1)
        pos=table(raw,10,m.materials);raw=raw[:pos]+rec.data()+raw[pos:]
        hatches+=1
    path.write_bytes(raw);verified=load(path)
    for _,n in walk(verified.root):
        if "mesh" not in n:continue
        tex=verified.textures[verified.materials[n["materials"][0]]["properties"]["_MainTex"]["index"]]["name"]
        if tex=="rwm_crest" and n["name"] not in {"RW_EndFaceBadges","RW_Ground_HatchCrest"} or ("label" in tex and role not in keep):
            assert all(len(set(tri))==1 for sub in n["mesh"]["submeshes"] for tri in sub)
    payload[key]=raw
    print(role,ends,"ends",bool(door is not None),"hatch",flush=True)
# Retain lettering on the five exempt identification plates. Their printed
# rooster medallion occupies the otherwise plain field above the divider.
for role in ("pwr","log","cen","nst","nsm"):
    key=modeldir+"rwm_"+role+"label.png"
    im=Image.open(io.BytesIO(payload[key]));w,h=im.size
    box=(round(w*.818),round(h*.20),round(w*.94),round(h*.433))
    fill=im.crop((round(.79*w),box[1],round(.79*w)+1,box[3])).resize((box[2]-box[0],box[3]-box[1]))
    im.paste(fill,box);out=io.BytesIO();im.save(out,format="PNG");payload[key]=out.getvalue()
version=prefix+"RoosterWorksGroundModules.version"
meta=json.loads(payload[version]);meta["VERSION"]["BUILD"]=38
payload[version]=(json.dumps(meta,indent=2)+"\n").encode()
target=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.38-Install.zip"
tmp=target.with_suffix(".partial")
with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for n,v in sorted(payload.items()):z.writestr(n,v)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None and all(z.read(n)==v for n,v in payload.items())
os.replace(tmp,target)
print("Verified",docks,"docking emblems and",hatches,"hatch emblems")

