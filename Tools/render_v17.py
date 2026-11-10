from pathlib import Path
import sys,math,copy
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load
from poses import flatten
import render_appearance as p
p.MODELS=R/'GameData/RoosterWorksGroundModules/Models';original_open=Image.open;lit=False
def shared(path,*args,**kwargs):
 candidate=Path(path)
 if lit and candidate.name=='rwm_endwindow.png':return Image.new('RGB',(32,32),(237,214,171))
 if not candidate.exists():candidate=CORE/'GameData/RoosterWorksStationModules/Models'/candidate.name
 return original_open(candidate,*args,**kwargs)
p.Image.open=shared
extent=0
def reader(path):
 model=load(path.parent/(path.stem.removesuffix('_250')+'.mu'))
 if model.name=='RW_GND_FLEX':
  for n in model.root['children']:
   if n['name']=='RW_TubeNose':n['position']=(.6+2.8*extent,0,0)
   if n['name']=='RW_TubeBellows':n['scale']=((.9+2.8*extent)/.9,1,1)
 return flatten(model)
p.load=reader
im=Image.new('RGB',(1500,720),(12,20,27));d=ImageDraw.Draw(im)
d.text((22,14),'ROOSTERWORKS / dev.17 / UPRIGHT END BADGES + WARM WINDOW LIGHTS',font=p.font(26,True),fill=(235,231,219))
for i,(role,on,title,theta) in enumerate([('HAB',False,'HAB / lights off',math.pi/2),('HAB',True,'HAB / lights on',math.pi/2),('ELB',True,'ELB / both badges above windows',.78)]):
 lit=on;pic=p.render('GND_'+role,size=(500,590),theta=theta,elevation=.12,span=3.8,emissive={'rwm_endwindow':1.0} if on else 0)
 im.paste(pic,(i*500,80));d.text((i*500+18,57),title,font=p.font(20),fill=(229,225,212))
d.text((22,678),'Native model geometry / emissive window glow approximation / in-game confirmation pending',font=p.font(21),fill=(194,203,200));im.save(R/'Previews/RoosterWorks-Ground-dev17-Lights.jpg',quality=95)
im=Image.new('RGB',(1500,750),(12,20,27));d=ImageDraw.Draw(im);d.text((22,14),'ROOSTERWORKS / FLEX-250 / COLLAPSIBLE CREW TUBE',font=p.font(28,True),fill=(235,231,219));lit=True
for i,t in enumerate((0,1)):
 extent=t;pic=p.render('GND_FLEX',size=(750,610),theta=1.0,elevation=.32,span=5.5,focus=(1.4*t,0,0),emissive={'rwm_endwindow':1.0});im.paste(pic,(i*750,80));d.text((i*750+25,57),'1.2 m collapsed' if t==0 else '4.0 m extended',font=p.font(22),fill=(229,225,212))
d.text((22,704),'2.5 m interfaces / two docking ports / no legs / moving end must be free before resizing',font=p.font(23),fill=(194,203,200));im.save(R/'Previews/RoosterWorks-Ground-dev17-Flex.jpg',quality=95)
print('Rendered upright badges, lights off/on and both native FLEX poses')
