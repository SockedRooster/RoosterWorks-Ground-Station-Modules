"""Add 22 outward docking frames to accepted models without changing meshes."""
from pathlib import Path
import sys,json,hashlib,math
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load
from native_derivatives import write
models=R/'GameData/RoosterWorksGroundModules/Models'
for path in sorted(models.glob('*.mu')):
 if path.stem=='RW_GND_END_250_125':continue # Mixed-size reducer owns its frames.
 report_path=R/'Reports'/(path.stem+'.json');report=json.loads(report_path.read_text())
 model=load(path);model.root['children']=[n for n in model.root['children'] if not n['name'].startswith('RW_Dock_')]
 ports=[]
 for key,value in report['nodes'].items():
  end=key.removeprefix('node_stack_');direction=value[3:6]
  # Local +Z points out of the face; local +Y stays vertical at every port.
  angle=math.atan2(direction[0],direction[2]);q=(0,math.sin(angle/2),0,math.cos(angle/2))
  name='RW_Dock_'+end
  model.root['children'].append(dict(name=name,position=tuple(value[:3]),rotation=q,scale=(1,1,1),children=[],tag='Untagged',layer=0))
  ports.append(dict(attachNode=end,transform=name,position=value[:3],forward=direction,up=[0,1,0]))
 write(model,path);report['docking_ports']=ports;report['native_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 report_path.write_text(json.dumps(report,indent=2)+'\n')
 print('Added',len(ports),'docking frames:',path.stem,flush=True)
