"""Inspection plate rendered from the shipped native models, not concept art."""
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
POSE=1
def reader(path):return flatten(load(path.parent/(path.stem.removesuffix('_250')+'.mu')),POSE)
p.load=reader
image=Image.new('RGB',(1200,1230),(12,20,27));draw=ImageDraw.Draw(image)
draw.text((24,16),'ROOSTERWORKS / GROUND v0.8.0-dev.6',font=p.font(26,True),fill=(235,232,220))
views=(('GRN','Horizontal growing beds',.10,.15,4.5,(0,-.2,0),1),('HAB','Windows clear of roof equipment',.2,1.4,5.2,(0,-.1,0),1),('HUB','Four-port underside service network',.65,-1,6.1,(0,-.5,0),1),('ELB','Continuous curved service lines',.6,-.8,4.9,(0,-.7,0),1),('HAB','Lower handrails / stairs raised',.6,.2,5.8,(0,-.4,0),0),('GRN','Distributed warm interior lighting',.1,.12,4.5,(0,-.2,0),1))
for i,(role,label,theta,elevation,span,focus,POSE) in enumerate(views):
 pic=p.render('GND_'+role,size=(600,350),theta=theta,elevation=elevation,span=span,focus=focus,point_lights=i==5,dark=i==5,emissive={'rwm_grnlamp':1,'rwm_grninspection':1})
 x=i%2*600;y=65+i//2*385;image.paste(pic,(x,y+24));draw.text((x+15,y),label,font=p.font(19,True),fill=(230,225,205));print('Rendered',label,flush=True)
image.save(R/'Previews/RoosterWorks-Ground-dev6-Refinements.jpg',quality=94)
