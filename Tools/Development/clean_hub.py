"""Remove the original graphite/bronze six-sided shoulder tubes and their clips."""
from build_exterior import here,scratch,modeldir,prefix,sdk,load,np,Buffer,struct,zipfile,json,os,sys
sys.path.insert(0,str(sdk/".build-deps"))
from build_ring_options import components

base=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.35-Install.zip"
key=modeldir+"RW_GND_HUB.mu"
file=scratch/"RW_GND_HUB.mu"
with zipfile.ZipFile(base) as z:
    payload={name:z.read(name) for name in z.namelist()}
raw=payload[key]
file.write_bytes(raw)
model=load(file)
# Preserve triangle numbering because the ring-color map indexes the shared meshes.
counts={}
for name,expected in [("bronze_1_0",144),("graphite_7_0",144),("steel_10_0",56)]:
    node=next(n for n in model.root["children"] if n["name"]=="GND_RW_Ground_"+name)
    mesh=node["mesh"]; verts=np.array(mesh["vertices"])
    indices=np.array(mesh["submeshes"][0],dtype="<i4")
    selected=[]
    for group in components(mesh):
        points=verts[np.unique(indices[group])]
        # Original looms sit on diagonal shoulders between the collars. The
        # cut-down ground shell also has cropped tube segments at its poles.
        if len(group) in (12,18) and np.all(abs(points)>.7) and abs(points).max()<1.595 and np.ptp(points,axis=0).max()<.27:
            selected.append(group)
    assert len(selected)==expected,(name,len(selected))
    counts[name]=len(selected)
    label=Buffer();label.s(node["name"])
    header=struct.pack("<ii",19,indices.size)
    pos=raw.index(header+indices.tobytes(),raw.index(label.data()))+len(header)
    rows=np.concatenate(selected)
    indices[rows]=indices[rows,0,None]
    raw=raw[:pos]+indices.tobytes()+raw[pos+indices.nbytes:]
    mesh["submeshes"][0]=list(map(tuple,indices.tolist()))
file.write_bytes(raw)
edited=load(file)
assert edited.root==model.root and edited.textures==model.textures and edited.materials==model.materials
payload[key]=raw
v=prefix+"RoosterWorksGroundModules.version"
meta=json.loads(payload[v]);meta["VERSION"]["BUILD"]=36
payload[v]=(json.dumps(meta,indent=2)+"\n").encode()
target=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.36-Install.zip"
tmp=target.with_suffix(".partial")
with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for n,data in sorted(payload.items()):z.writestr(n,data)
with zipfile.ZipFile(tmp) as z, zipfile.ZipFile(base) as old:
    assert z.testzip() is None and set(z.namelist())==set(old.namelist())
    assert {n for n in z.namelist() if z.read(n)!=old.read(n)}=={key,v}
os.replace(tmp,target)
print("Removed old loom segments and clips:",counts)
