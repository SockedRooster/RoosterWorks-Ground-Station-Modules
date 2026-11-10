from pathlib import Path
import sys,math
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
import render_appearance as p
from native_model import load
from poses import flatten
p.MODELS=R/'GameData/RoosterWorksGroundModules/Models'
def reader(path):return flatten(load(path.parent/(path.stem.removesuffix('_250')+'.mu')))
p.load=reader
im=Image.new('RGB',(1200,990),(12,20,27));draw=ImageDraw.Draw(im)
draw.text((22,15),'ROOSTERWORKS / GROUND v0.8.0-dev.12',font=p.font(28,True),fill=(234,230,215))
views=(('GRN','Lighting in every shelf cavity',.05,.12,4.4,True),('GRN','Greenhouse / roof handrails restored',.4,1.05,5.0,False),('PWR','Power / roof handrails restored',.5,.9,4.2,False),('ELB','Elbow / yellow roof handrails',.65,1.0,5.0,False))
for i,(role,label,theta,elevation,span,night) in enumerate(views):
 pic=p.render('GND_'+role,size=(600,420),theta=theta,elevation=elevation,span=span,focus=(0,-.3,0),dark=night,point_lights=night,emissive={'rwm_grnlamp':1,'rwm_grninspection':1})
 x=i%2*600;y=70+i//2*455;im.paste(pic,(x,y+24));draw.text((x+16,y),label,font=p.font(20,True),fill=(232,226,209));print('Rendered',label,flush=True)
im.save(R/'Previews/RoosterWorks-Ground-dev12-Roof-Handrails.jpg',quality=94)
