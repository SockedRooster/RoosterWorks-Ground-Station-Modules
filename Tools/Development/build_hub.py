"""Route the four ground hub ports and remove its three-layer nameplate."""
from build_exterior import (here,scratch,modeldir,prefix,Mesh,tube,load,np,math,
                           Buffer,append_hardware,struct,zipfile,json,os)
from native_model import walk

base=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.34-Install.zip"
with zipfile.ZipFile(base) as archive:
    payload={name:archive.read(name) for name in archive.namelist()}
hub="RW_GND_HUB"
path=scratch/(hub+".mu")
key=modeldir+path.name
raw=payload[key]
path.write_bytes(raw)
model=load(path)
# Match the original three analytic plaque surfaces by material and cylindrical
# profile. Preserve triangle slots used by the ring-colour selector.
layers={"rwm_hublabel":(.86,.36,1.263),"rwm_bronze":(.91,.40,1.257),"rwm_graphite":(.96,.44,1.25)}
removed={}
for _,node in walk(model.root):
    if "mesh" not in node:continue
    for idx,triangles in zip(node["materials"],node["mesh"]["submeshes"]):
        mat=model.materials[idx]["properties"]["_MainTex"]["index"]
        texture=model.textures[mat]["name"]
        if texture not in layers:continue
        width,height,r=layers[texture]
        v=np.asarray(node["mesh"]["vertices"])
        match=(np.abs(np.abs(v[:,0])-width/2)<.0001)&(abs(v[:,1]-1.48)<height/2+.0001)&(v[:,2]<0)&(abs(np.hypot(v[:,1]-1.48,v[:,2])-r)<.0001)
        hits=np.flatnonzero(np.all(match[np.asarray(triangles)],axis=1))
        if not len(hits):continue
        assert len(hits)==24 and texture not in removed
        header=Buffer();header.s(node["name"])
        start=raw.index(header.data())
        encoded=np.asarray(triangles,dtype="<i4")
        record=struct.pack("<ii",19,encoded.size)+encoded.tobytes()
        pos=raw.index(record,start)+8
        encoded[hits]=encoded[hits,0,None]
        raw=raw[:pos]+encoded.tobytes()+raw[pos+encoded.nbytes:]
        removed[texture]=len(hits)
assert removed.keys()==layers.keys(),removed

tris=[]
for node in model.root["children"]:
    if "mesh" not in node:continue
    assert node["position"]==(0,0,0) and node["rotation"]==(0,0,0,1)
    verts=np.asarray(node["mesh"]["vertices"])
    for sub in node["mesh"]["submeshes"]:tris.extend(verts[np.asarray(sub)])
tri=np.array(tris)
# Upward-facing roof with overhangs sampled from above.
a,b,c=tri.transpose(1,0,2)
ab=b-a;ac=c-a
det=ab[:,0]*ac[:,2]-ac[:,0]*ab[:,2]
det[abs(det)<1e-10]=np.nan
def roof(x,z):
    dx=x-a[:,0];dz=z-a[:,2]
    u=(dx*ac[:,2]-dz*ac[:,0])/det
    v=(dz*ab[:,0]-dx*ab[:,2])/det
    mask=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)
    return max((a[:,1]+u*ab[:,1]+v*ac[:,1])[mask])

def sweep(mesh,centers,width):
    rings=[]
    for i,p in enumerate(centers):
        t=centers[min(i+1,len(centers)-1)]-centers[max(i-1,0)]
        t/=np.linalg.norm(t)
        side=np.cross(t,[0,1,0]);side/=np.linalg.norm(side)
        up=np.cross(t,side)
        ring=[]
        for j in range(12):
            angle=j*math.tau/12
            n=side*math.cos(angle)+up*math.sin(angle)
            ring.append((p+width*n,n))
        rings.append(ring)
    for row,nxt in zip(rings,rings[1:]):
        for j in range(12):
            k=(j+1)%12
            quad=[row[j],row[k],nxt[k],nxt[j]]
            mesh.quad([p for p,n in quad],[n for p,n in quad])

groups=[(n,k,Mesh()) for n,k in [("Handrails","rail"),("BlueLoom","service_blue"),("YellowLoom","service_yellow"),("MountingFeet","graphite"),("CableClips","steel")]]
for sx in (-1,1):
    for sz in (-1,1):
        for row,(degrees,r,w) in enumerate([(72,1.315,.017),(76,1.30,.009),(78,1.30,.009)]):
            angle=math.radians(degrees)
            d=r*math.cos(angle); y=r*math.sin(angle)
            # A straight terminal on both ends, joined by a single smooth shoulder bend.
            ts=np.linspace(0,1,49)
            def coord(t):return (1-t)**3*1.92+3*(1-t)**2*t*1.62+(3*(1-t)*t*t+t**3)*d
            pts=np.array([[2*sx,y,sz*d]]+[[sx*coord(t),y,sz*coord(1-t)] for t in ts]+[[sx*d,y,2*sz]])
            h=np.array([roof(x,z) for x,_,z in pts[1:-1]])
            weights=np.sin(math.pi*ts)**2
            safe=w+.014
            assert all(y-h[[0,-1]]>=safe)
            delta=max((h[1:-1]+safe-y)/weights[1:-1])
            # Keep each run level where the sampled surface permits.
            pts[1:-1,1]+=max(0,delta)*weights
            assert min(pts[1:-1,1]-h)>w and max(pts[:,1])<1.65
            sweep(groups[row][2],pts,w)
            for i in (4,14,25,36,46):
                p=pts[i];foot=p.copy();foot[1]=h[i-1]
                vert=np.array([0,1,0]);t=pts[i+1]-pts[i-1];t/=np.linalg.norm(t)
                tube(groups[3][2],foot-.010*vert,foot+.006*vert,.037 if row==0 else .019,12)
                tube(groups[4][2],foot,p,.013 if row==0 else .008,10)
                tube(groups[4][2],p-.022*t,p+.022*t,w+.003,12)

data=append_hardware(raw,model,groups)
path.write_bytes(data)
check=load(path)
assert len(check.root["children"])==len(model.root["children"])+5
payload[key]=data
version=prefix+"RoosterWorksGroundModules.version"
meta=json.loads(payload[version]);meta["VERSION"]["BUILD"]=35
payload[version]=(json.dumps(meta,indent=2)+"\n").encode()
out=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.35-Install.zip"
tmp=out.with_suffix(".partial")
with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for n,data in sorted(payload.items()):z.writestr(n,data)
with zipfile.ZipFile(tmp) as z:
    assert len(z.namelist())==len(payload) and all(z.read(n)==v for n,v in payload.items())
os.replace(tmp,out)
print("Verified 12 routes and all three removed plaque layers.")
