"""Read-only poses for preview and drill-clearance checks."""
import copy,math
import numpy as np
from native_model import walk

def rotation(q):
 q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q);x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def matrices(root):
 out={}
 def rec(n,parent):
  m=np.eye(4);m[:3,:3]=rotation(n['rotation'])@np.diag(n['scale']);m[:3,3]=n['position'];m=parent@m
  out[id(n)]=m
  for c in n['children']:rec(c,m)
 rec(root,np.eye(4));return out

def stock_pose(original,fraction):
 m=copy.deepcopy(original);m.root['position']=(0,0,0)
 for _,n in walk(m.root):
  if 'animation' not in n:continue
  clip=next(c for c in n['animation']['clips'] if c['name']=='Drill_Deploy')
  paths={p.removeprefix('/'+n['name']).lstrip('/'):node for p,node in walk(n)}
  end=max(key[0] for c in clip['curves'] for key in c['keys']);t=end*fraction
  for c in clip['curves']:
   if c['path'] not in paths:continue
   prop=c['property'];base,_,component=prop.rpartition('.')
   key={'m_LocalPosition':'position','m_LocalRotation':'rotation','m_LocalScale':'scale'}.get(base)
   if key is None:continue
   keys=c['keys'];value=keys[-1][1]
   if t<=keys[0][0]:value=keys[0][1]
   else:
    for a,b in zip(keys,keys[1:]):
     if a[0]<=t<=b[0]:
      dt=b[0]-a[0];s=0 if dt==0 else (t-a[0])/dt
      # Unity float animation uses Hermite tangents; infinite is stepped.
      value=a[1] if not math.isfinite(a[3]) else (2*s**3-3*s*s+1)*a[1]+(s**3-2*s*s+s)*dt*a[3]+(-2*s**3+3*s*s)*b[1]+(s**3-s*s)*dt*b[2]
      break
   target=paths[c['path']];values=list(target[key]);values['xyzw'.index(component)]=value;target[key]=values
 worlds=matrices(m.root);nodes={n['name']:n for _,n in walk(m.root)}
 # Skin only for the ephemeral preview/clearance copy. No stock mesh is saved.
 for _,n in walk(m.root):
  mesh=n.get('mesh',{})
  if not mesh.get('weights'):continue
  transforms=[]
  for name,bp in zip(n['bones'],mesh['bindposes']):
   # MU serializes bind-pose matrix rows in sequence.
   transforms.append(np.linalg.inv(worlds[id(n)])@worlds[id(nodes[name])]@np.array(bp).reshape(4,4))
  verts=[];normals=[]
  for v,normal,weights in zip(mesh['vertices'],mesh['normals'],mesh['weights']):
   transform=sum((w*transforms[index] for index,w in weights if w),np.zeros((4,4)))
   verts.append(tuple((transform@np.array((*v,1)))[:3]));nv=transform[:3,:3]@normal;normals.append(tuple(nv/max(np.linalg.norm(nv),1e-15)))
  mesh['vertices']=verts;mesh['normals']=normals
 # MODEL half-scale, rotation +90 Y and offset +.05 Z, as shipped.
 m.root['rotation']=(0,math.sin(math.pi/4),0,math.cos(math.pi/4));m.root['position']=(0,0,.05);m.root['scale']=(.5,.5,.5)
 return m

def points(model):
 world=matrices(model.root);out=[]
 for _,n in walk(model.root):
  if 'mesh' in n:
   v=np.array(n['mesh']['vertices']);mt=world[id(n)];out.append(v@mt[:3,:3].T+mt[:3,3])
 return np.concatenate(out)
