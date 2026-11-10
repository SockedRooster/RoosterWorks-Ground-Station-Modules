from pathlib import Path
import json,math,numpy as np
R=Path(__file__).resolve().parents[1]
def rotation(q):
 x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def world_nodes(model,progress=1):
 report=json.loads((R/f'Reports/{model.name}.json').read_text());bindings={b['name']:b for b in report['motion']};s=progress*progress*(3-2*progress)
 def walk(n,parent):
  position=n['position'];q=n['rotation']
  if n['name'] in bindings:
   b=bindings[n['name']];position=(1-s)*np.array(b['retractPosition'])+s*np.array(b['position']);angle=math.radians(b['retractEuler'][0]*(1-s))/2;q=(math.sin(angle),0,0,math.cos(angle))
  m=np.eye(4);m[:3,:3]=rotation(q)@np.diag(n['scale']);m[:3,3]=position;m=parent@m
  yield n,m
  for child in n['children']:yield from walk(child,m)
 return walk(model.root,np.eye(4))
def flatten(model,progress=1):
 for n,m in list(world_nodes(model,progress)):
  if 'mesh' in n:
   mesh=n['mesh'];v=np.array(mesh['vertices']);mesh['vertices']=(v@m[:3,:3].T+m[:3,3]).tolist()
   normal=np.array(mesh['normals'])@np.linalg.inv(m[:3,:3]);normal/=np.linalg.norm(normal,axis=1)[:,None];mesh['normals']=normal.tolist()
   n['position']=(0.,0.,0.);n['rotation']=(0.,0.,0.,1.);n['scale']=(1.,1.,1.)
  elif 'light' in n:n['position']=tuple(m[:3,3])
 return model
