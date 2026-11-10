"""Repair end badges in world-up coordinates and give portholes emissive glass."""
from pathlib import Path
import sys,math,json,copy,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5';OLD=W/'ground-hotpatch-v16';GD=R/'GameData/RoosterWorksGroundModules';OUT=GD/'Models'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from native_model import load,walk
from native_derivatives import write
from config_nodes import parse,dump,Node
import build_hab250 as h
def compact(mesh,keep):
 tris=[t for t,k in zip(mesh['submeshes'][0],keep) if k];used=sorted({i for t in tris for i in t});remap={i:j for j,i in enumerate(used)}
 for key in ('vertices','normals','uvs','uv2','tangents','colors'):
  if key in mesh:mesh[key]=[mesh[key][i] for i in used]
 mesh['submeshes']=[[tuple(remap[i] for i in t) for t in tris]]
def native(name,mesh,material):return dict(name=name,position=(0,0,0),rotation=(0,0,0,1),scale=(1,1,1),children=[],tag='Untagged',layer=0,mesh=dict(vertices=mesh.vertices,normals=mesh.normals,uvs=mesh.uvs,submeshes=[mesh.triangles]),materials=[material],shadows=(1,1))
def repair(model,part):
 ends=[]
 for key,value in part.values:
  if key.startswith('node_stack_'):
   a=np.array([float(v) for v in value.split(',')]);ends.append((key,a[:3],a[3:6]))
 windows=h.Mesh();badges=h.Mesh();removed={'crest':0,'window':0};body_turns=0
 crest_index=next(i for i,m in enumerate(model.materials) if model.textures[m['properties']['_MainTex']['index']]['name']=='rwm_crest')
 for _,n in list(walk(model.root)):
  if 'mesh' not in n:continue
  mesh=n['mesh'];tex=model.textures[model.materials[n['materials'][0]]['properties']['_MainTex']['index']]['name']
  if tex not in ('rwm_crest','rwm_black'):continue
  assert n['position']==(0.,0.,0.) and n['rotation']==(0.,0.,0.,1.),n['name']
  keep=[]
  for tri in mesh['submeshes'][0]:
   p=np.array([mesh['vertices'][i] for i in tri]);normal=np.array([mesh['normals'][i] for i in tri]).mean(0);remove=False
   for _,center,outward in ends:
    q=p-center;depth=q@outward;radial=q-depth[:,None]*outward
    limit=.45 if tex=='rwm_crest' else .106
    if np.all(abs(depth)<.085) and np.all(np.linalg.norm(radial,axis=1)<limit+.0001) and np.dot(normal,outward)>.9:
     remove=True;removed['crest' if tex=='rwm_crest' else 'window']+=1;break
   keep.append(not remove)
  compact(mesh,keep)
  if tex=='rwm_crest' and part.get('name') in ('RW_GND_HAB','RW_GND_AIR','RW_GND_CMD'):
   mesh['uvs']=[(1-v,u) for u,v in mesh['uvs']];body_turns+=len(mesh['uvs'])
 for key,center,outward in ends:
  right=-np.cross((0,1,0),outward);up=np.array((0,1,0))
  # Clock position and UV direction are independently world-up for every end.
  c=center-outward*.023+up*.27
  points=[tuple(c+right*.085*a+up*.085*b) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))]
  badges.quad(points,[tuple(outward)]*4,reverse=True)
  # Overlap the surrounding aperture by 1 mm, avoiding a see-through hairline.
  c=center-outward*.022;r=.091 if part.get('name')=='RW_GND_END_250_125' and key=='node_stack_top' else .105
  for j in range(64):
   a=j*math.tau/64;b=(j+1)*math.tau/64
   points=[tuple(c),tuple(c+r*(right*math.cos(a)+up*math.sin(a))),tuple(c+r*(right*math.cos(b)+up*math.sin(b)))]
   windows.triangle(points,[tuple(outward)]*3,[(.5,.5),(.5+.5*math.cos(a),.5+.5*math.sin(a)),(.5+.5*math.cos(b),.5+.5*math.sin(b))])
  # Fix outward winding for Unity while retaining outward-readable UV axes.
 for mesh in (windows,badges):
  v=np.array(mesh.vertices);norm=np.array(mesh.normals)
  mesh.triangles=[tuple(reversed(t)) if np.dot(np.cross(v[t[1]]-v[t[0]],v[t[2]]-v[t[0]]),norm[list(t)].mean(0))<0 else t for t in mesh.triangles]
 material=copy.deepcopy(model.materials[crest_index]);material['name']='RW_EndWindowGlass';material['shader']='KSP/Emissive/Diffuse'
 diffuse=len(model.textures);model.textures.append(dict(name='rwm_endwindow',type=0));emission=len(model.textures);model.textures.append(dict(name='rwm_endwindow_emissive',type=0))
 material['properties']={'_Color':(1,1,1,1),'_MainTex':dict(index=diffuse,scale=(1,1),offset=(0,0)),'_Emissive':dict(index=emission,scale=(1,1),offset=(0,0)),'_EmissiveColor':(0,0,0,1)}
 mi=len(model.materials);model.materials.append(material)
 model.root['children'] += [native('RW_EndFaceBadges',badges,crest_index),native('RW_EndWindows',windows,mi)]
 # Empty old crest batches are harmless but omitted for finite mesh validation.
 def remove_empty(n):
  for c in n['children']:remove_empty(c)
  n['children']=[c for c in n['children'] if not ('mesh' in c and not c['mesh']['vertices'])]
 remove_empty(model.root)
 changers=[n for n in part.children if n.get('name')=='ModuleColorChanger' and 'GrowLights' not in (n.get('moduleID') or '')]
 if changers:changers[0].values.append(('includedRenderer','RW_EndWindows'))
 elif part.get('name')=='RW_GND_GRN':part.children.append(Node('MODULE',[('name','ModuleRWEndWindowLink'),('sourceLightName','RW_GreenhouseInspectionLight')]))
 else:
  part.children.append(Node('MODULE',[('name','ModuleColorChanger'),('moduleID',part.get('name')+'_EndLights'),('shaderProperty','_EmissiveColor'),('animRate','.65'),('animState','false'),('useRate','true'),('toggleInEditor','true'),('toggleInFlight','true'),('toggleName','Toggle Module Lights'),('eventOnName','Module Lights On'),('eventOffName','Module Lights Off'),('includedRenderer','RW_EndWindows'),('toggleAction','True'),('defaultActionGroup','Light')],[Node('redCurve',[('key','0 0'),('key','1 .93')]),Node('greenCurve',[('key','0 0'),('key','1 .84')]),Node('blueCurve',[('key','0 0'),('key','1 .67')]),Node('alphaCurve',[('key','0 1'),('key','1 1')])]))
 return dict(ends=[dict(name=k,center=c.tolist(),outward=n.tolist()) for k,c,n in ends],removed=removed,body_badge_vertices_turned_90=body_turns)
def main():
 Image.new('RGB',(32,32),(19,29,35)).save(OUT/'rwm_endwindow.png');Image.new('RGB',(32,32),(255,255,255)).save(OUT/'rwm_endwindow_emissive.png')
 audit={}
 for path in sorted((OLD/'GameData/RoosterWorksGroundModules/Parts').glob('*.cfg')):
  root=parse(path.read_text(encoding='utf-8'));part=root.children[0];ID=part.get('name');model=load(OLD/f'GameData/RoosterWorksGroundModules/Models/{ID}.mu')
  audit[ID]=repair(model,part);write(model,OUT/(ID+'.mu'));(GD/'Parts'/path.name).write_text(dump(root),encoding='utf-8')
  report_path=R/f'Reports/{ID}.json';report=json.loads(report_path.read_text());report['triangles']=sum(len(s) for _,n in walk(model.root) if 'mesh' in n for s in n['mesh']['submeshes']);report['end_face_refinement']=audit[ID];report['native_sha256']=hashlib.sha256((OUT/(ID+'.mu')).read_bytes()).hexdigest();report_path.write_text(json.dumps(report,indent=2)+'\n')
  print('Repaired badges/windows:',ID,len(audit[ID]['ends']),'ends',audit[ID]['removed'],flush=True)
 (R/'Reports/END_FACE_REFINEMENTS.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__':main()
