"""Extend dev.36's standard shoulder routes to the greenhouse and 90-degree elbow."""
from build_exterior import (here,scratch,modeldir,prefix,files,skin_sampler,append_hardware,
                            load,shell_triangles,Mesh,tube,np,math,json,zipfile,os)

with zipfile.ZipFile(here/"RoosterWorks-Ground-Modules-v0.8.0-dev.36-Install.zip") as archive:
    payload={n:archive.read(n) for n in archive.namelist()}

def key(role):
    return modeldir+"RW_GND_"+role+".mu"

# Match the same curves, radii and model-space normals at either mating face.
def elbow_frame(distance):
    bend=1.8
    s=distance-.3
    a=min(math.pi/2,max(0,s/bend))
    radial=np.array([-math.cos(a),0,-math.sin(a)])
    along=np.array([math.sin(a),0,-math.cos(a)])
    center=np.array([.9,0,.9])+bend*radial
    center+=along*(s-a*bend)
    return center,radial,along

def top_surface(tris,x,z):
    a,b,c=tris.transpose(1,0,2)
    ab=b-a;ac=c-a
    det=ab[:,0]*ac[:,2]-ab[:,2]*ac[:,0]
    det[abs(det)<1e-10]=np.nan
    dx=x-a[:,0];dz=z-a[:,2]
    u=(dx*ac[:,2]-dz*ac[:,0])/det
    v=(dz*ab[:,0]-dx*ab[:,2])/det
    inside=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)
    return float(max((a[:,1]+u*ab[:,1]+v*ac[:,1])[inside]))

def make_elbow():
    path=scratch/"RW_GND_ELB.mu"
    raw=payload[key("ELB")];path.write_bytes(raw);model=load(path)
    tris=shell_triangles(model)
    groups=[(n,k,Mesh()) for n,k in (("Handrails","rail"),("BlueLoom","service_blue"),
            ("YellowLoom","service_yellow"),("MountingFeet","graphite"),("CableClips","steel"))]
    length=.6+1.8*math.pi/2
    up=np.array([0.,1.,0.])
    for sign in (-1,1):
        for idx,(angle,r,width) in enumerate(((72,1.315,.017),(76,1.30,.009),(78,1.30,.009))):
            angle=math.radians(angle)
            h=r*math.sin(angle); side=sign*r*math.cos(angle)
            prev=None
            for s in np.r_[0,np.linspace(.3,length-.3,65),length]:
                center,radial,along=elbow_frame(s)
                p=center+side*radial+h*up
                ring=[]
                for j in range(12):
                    t=j*math.tau/12
                    n=math.cos(t)*up+math.sin(t)*radial
                    ring.append((p+width*n,n))
                if prev:
                    for j in range(12):
                        k=(j+1)%12
                        quad=(prev[j],prev[k],ring[k],ring[j])
                        if np.dot(np.cross(quad[1][0]-quad[0][0],quad[2][0]-quad[0][0]),quad[0][1])<0:
                            quad=quad[::-1]
                        groups[idx][2].quad([v for v,n in quad],[n for v,n in quad])
                prev=ring
                if 0<s<length:
                    assert top_surface(tris,p[0],p[2])+width < h
            for s in np.linspace(.105,length-.105,9):
                center,radial,along=elbow_frame(s)
                p=center+side*radial+h*up
                foot=p.copy();foot[1]=top_surface(tris,p[0],p[2])
                tube(groups[3][2],foot-.012*up,foot+.006*up,.035 if idx==0 else .019,12)
                tube(groups[4][2],foot,p,.014 if idx==0 else .008,10)
                tube(groups[4][2],p-.023*along,p+.023*along,width+.003,12)
    data=append_hardware(raw,model,groups);path.write_bytes(data)
    assert load(path).root["children"][:-5]==model.root["children"]
    return data

assert payload[key("GRN")]==files[key("GRN")]
def make_greenhouse():
    path=scratch/"RW_GND_GRN.mu"
    raw=payload[key("GRN")];path.write_bytes(raw);model=load(path)
    frame=shell_triangles(model)
    glass=[n["mesh"] for n in model.root["children"] if "grnglass" in n["name"]]
    assert glass
    obstacles=np.concatenate([frame]+[np.asarray(m["vertices"])[np.asarray(sub)] for m in glass for sub in m["submeshes"]])
    groups=[(n,k,Mesh()) for n,k in (("Handrails","rail"),("BlueLoom","service_blue"),
            ("YellowLoom","service_yellow"),("MountingFeet","graphite"),("CableClips","steel"))]
    end=1.8
    for sign in (-1,1):
        for idx,(angle,r,width) in enumerate(((72,1.315,.017),(76,1.30,.009),(78,1.30,.009))):
            a=math.radians(angle);normal=np.array([0,math.sin(a),sign*math.cos(a)])
            skin=skin_sampler(frame,normal);outer=skin_sampler(obstacles,normal)
            axis=np.array([1,0,0])
            tube(groups[idx][2],-end*axis+r*normal,end*axis+r*normal,width,12)
            for x in np.linspace(-end+.002,end-.002,253):
                assert outer(x)+width<r
            # Attach only to opaque frame ribs and collars. Skip the glazed bays.
            for x in (-1.66,-1.25,0,1.25,1.66):
                candidates=sorted(np.linspace(x-.095,x+.095,77),key=lambda v:abs(v-x))
                for pos in candidates:
                    try: high=skin(pos)
                    except ValueError:continue
                    if high>=1.195 and abs(high-outer(pos))<.0001:break
                else:raise ValueError(("missing glazing rib",x))
                foot=pos*axis+high*normal;top=pos*axis+r*normal
                tube(groups[3][2],foot-.009*normal,foot+.006*normal,.036 if idx==0 else .019,12)
                tube(groups[4][2],foot,top,.014 if idx==0 else .008,10)
                tube(groups[4][2],top-.022*axis,top+.022*axis,width+.003,12)
    raw=append_hardware(raw,model,groups);path.write_bytes(raw)
    assert load(path).root["children"][:-5]==model.root["children"]
    return raw
payload[key("GRN")]=make_greenhouse()
payload[key("ELB")]=make_elbow()
# Check native vertices on both terminal planes against dev.36's straight tube.
def ends(role):
    path=scratch/("RW_GND_"+role+".mu");path.write_bytes(payload[key(role)])
    m=load(path)
    for n in m.root["children"][-5:-2]:
        vertices=np.array(n["mesh"]["vertices"])
        for ax in ([0,2] if role=="ELB" else [0,0]):
            if role=="ELB":
                end=1.2;shift=-.9
            else:
                end=vertices[:,0].max();shift=0
            p=vertices[np.isclose(vertices[:,ax],end,atol=2e-6)]
            if role!="ELB":
                other=vertices[np.isclose(vertices[:,0],-end)]
                assert sorted(set(map(tuple,p[:,1:])))==sorted(set(map(tuple,other[:,1:])))
            side=p[:,2 if ax==0 else 0]-shift
            # Rings can have different angular tessellation; check both cable centers.
            yield np.array([[np.unique(p[side*sign>0,1]).mean(),(side[side*sign>0].max()+side[side*sign>0].min())/2] for sign in (-1,1)])
for role in ("ELB","GRN"):
    for actual,reference in zip(ends(role),ends("TUB"),strict=True):
        assert np.allclose(actual,reference,atol=2e-6),(role,actual,reference)
version=prefix+"RoosterWorksGroundModules.version"
meta=json.loads(payload[version]);meta["VERSION"]["BUILD"]=37
payload[version]=(json.dumps(meta,indent=2)+"\n").encode()
target=here/"RoosterWorks-Ground-Modules-v0.8.0-dev.37-Install.zip"
tmp=target.with_suffix(".partial")
with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for n,v in sorted(payload.items()):z.writestr(n,v)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None and all(z.read(n)==v for n,v in payload.items())
os.replace(tmp,target)
print("Verified all elbow and greenhouse terminal centers against the crew tube.")


