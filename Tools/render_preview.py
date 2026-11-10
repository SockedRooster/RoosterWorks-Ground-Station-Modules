"""Inspect exported KSP meshes/textures directly without reopening/editing models."""
from pathlib import Path
import sys,numpy as np,math
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
import render_appearance as p
from native_model import load,walk
from poses import flatten
models=R/'GameData/RoosterWorksGroundModules/Models';p.MODELS=models
POSE=1
def reader(path):
    m=load(path.parent/(path.stem.removesuffix('_250')+'.mu'))
    for t in m.textures:t['name']=t['name'].rsplit('/',1)[-1]
    return flatten(m,POSE)
p.load=reader
image=Image.new('RGB',(1440,1570),(12,20,27));d=ImageDraw.Draw(image)
d.text((25,15),'ROOSTERWORKS / GROUND MODULE HOT PATCH',font=p.font(30,True),fill=(232,232,218))
d.text((25,57),'Actual native models / upper windows / animated legs and access stairs',font=p.font(18),fill=(161,180,190))
for i,role in enumerate(('HAB','LAB','CMD','LOG','GRN','AIR','PWR','HUB','TUB','ELB')):
    m=flatten(load(models/f'RW_GND_{role}.mu'));v=np.array([v for _,n in walk(m.root) if 'mesh' in n for v in n['mesh']['vertices']])
    view=np.array((math.sin(.7),.4,math.cos(.7)));view/=np.linalg.norm(view);right=-np.cross((0,1,0),view);right/=np.linalg.norm(right);up=np.cross(right,view)
    vx=v@right;vy=v@up;focus=(vx.min()+vx.max())/2*right+(vy.min()+vy.max())/2*up
    span=max(vy.max()-vy.min(),(vx.max()-vx.min())*.93)*1.18
    pic=p.render('GND_'+role,size=(480,330),span=span,theta=.7,elevation=.4,focus=focus)
    x=i%3*480;y=105+i//3*355;image.paste(pic,(x,y+25));d.text((x+20,y),role+' / Ground',font=p.font(22,True),fill=(231,226,208));print('Preview',role,flush=True)
(R/'Previews').mkdir(exist_ok=True);image.save(R/'Previews/RoosterWorks-Ground-HotPatch-Native-Preview.jpg',quality=92)
comparison=Image.new('RGB',(1440,1020),(12,20,27));d=ImageDraw.Draw(comparison)
d.text((20,15),'DEPLOYMENT / LOWERED AND RAISED POSES',font=p.font(28,True),fill=(230,230,218))
for row,role in enumerate(('HAB','CMD','HUB')):
 for col,POSE in enumerate((1,0)):
  pic=p.render('GND_'+role,size=(720,300),span=6.5,theta=.7,elevation=.3,focus=(0,-.3,0))
  comparison.paste(pic,(col*720,70+row*315));d.text((col*720+20,50+row*315),role+(' / Lowered' if POSE else ' / Raised'),font=p.font(20),fill=(231,226,208))
comparison.save(R/'Previews/RoosterWorks-Ground-Deployment-Poses.jpg',quality=93)
POSE=1
back=p.render('GND_HAB',size=(1000,720),span=5.2,theta=math.pi+.3,elevation=.12,focus=(0,-.35,0))
back.save(R/'Previews/RoosterWorks-Ground-Horizontal-Label.jpg',quality=93)
frames=[]
for POSE in (0,.2,.4,.6,.8,1):
 frames.append(p.render('GND_HAB',size=(360,360),span=6.5,theta=.7,elevation=.3,focus=(0,-.3,0)).convert('RGB'))
frames=frames+list(reversed(frames[1:-1]))
frames[0].save(R/'Previews/RoosterWorks-Ground-Deployment.gif',save_all=True,append_images=frames[1:],duration=[900]+[500]*4+[900]+[500]*4,loop=0)
