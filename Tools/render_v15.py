from pathlib import Path
import sys,math
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
from native_model import load
from poses import flatten
import render_appearance as p
p.MODELS=R/'GameData/RoosterWorksGroundModules/Models';original_open=Image.open
def shared(path,*args,**kwargs):
 candidate=Path(path)
 if not candidate.exists():candidate=CORE/'GameData/RoosterWorksStationModules/Models'/candidate.name
 return original_open(candidate,*args,**kwargs)
p.Image.open=shared
def reader(path):return flatten(load(path.parent/(path.stem.removesuffix('_250')+'.mu')))
p.load=reader
image=Image.new('RGB',(1650,760),(12,20,27));d=ImageDraw.Draw(image)
d.text((22,15),'ROOSTERWORKS / dev.15 / ENDCAP, PWR AND ELB ARTWORK',font=p.font(30,True),fill=(236,231,217))
for i,(role,theta,elevation,span,title) in enumerate([('END_250_125',math.pi/2,.12,2.9,'1.25 m nose / clean hatch and logo'),('PWR',math.pi,.18,3.9,'PWR / lowered complete nameplate'),('ELB',.78,.35,4.0,'ELB / rooster rotated 270 degrees')]):
 pic=p.render('GND_'+role,size=(550,620),theta=theta,elevation=elevation,span=span,focus=(0,0,0))
 image.paste(pic,(i*550,90));d.text((i*550+16,64),title,font=p.font(19),fill=(227,225,215))
d.text((22,717),'Native exported geometry and textures / one docking port on endcap / in-game confirmation pending',font=p.font(22),fill=(194,204,201))
image.save(R/'Previews/RoosterWorks-Ground-dev15-Artwork.jpg',quality=95)
print('Rendered final native endcap, lowered PWR badge and rotated ELB symbols')
