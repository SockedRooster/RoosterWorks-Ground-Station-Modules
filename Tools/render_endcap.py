from pathlib import Path
import sys,math
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
import render_appearance as p
from native_model import load
from poses import flatten
p.MODELS=R/'GameData/RoosterWorksGroundModules/Models'
original_open=Image.open
def shared_open(path,*args,**kwargs):
 candidate=Path(path)
 if not candidate.exists() and candidate.suffix=='.png':candidate=CORE/'GameData/RoosterWorksStationModules/Models'/candidate.name
 return original_open(candidate,*args,**kwargs)
p.Image.open=shared_open
def reader(path):return flatten(load(path.parent/(path.stem.removesuffix('_250')+'.mu')))
p.load=reader
im=Image.new('RGB',(1500,700),(12,20,27));draw=ImageDraw.Draw(im)
draw.text((25,15),'ROOSTERWORKS / END-250/125 / ROUNDED DOCKING ENDCAP',font=p.font(28,True),fill=(236,232,218))
for i,(theta,title,finish) in enumerate(((1.25,'1.25 m nose / White','White'),(.55,'Rounded shoulder / Grey metal','Grey metal'),(-1.3,'2.5 m rear interface / White','White'))):
 pic=p.render('GND_END_250_125',size=(500,560),theta=theta,elevation=.30,span=3.0,finish=finish)
 im.paste(pic,(i*500,75));draw.text((i*500+18,60),title,font=p.font(19,True),fill=(230,226,211))
draw.text((25,650),'0.9 m long | 2.5 m + 1.25 m docking | Crossfeed always on | No staging',font=p.font(23),fill=(193,201,199))
im.save(R/'Previews/RoosterWorks-Ground-Endcap-250-125.jpg',quality=94)
print('Rendered native endcap preview')
