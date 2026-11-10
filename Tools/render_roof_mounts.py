from pathlib import Path
import sys
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path[:0]=[str(CORE/'Tools'),str(CORE/'Source')]
import render_appearance as p
from native_model import load
from poses import flatten
p.MODELS=R/'GameData/RoosterWorksGroundModules/Models'
def reader(path):return flatten(load(path.parent/(path.stem.removesuffix('_250')+'.mu')))
p.load=reader
im=Image.new('RGB',(1200,810),(12,20,27));d=ImageDraw.Draw(im);d.text((20,14),'ROOSTERWORKS / ROOF HANDRAIL SOCKETS / dev.13',font=p.font(27,True),fill=(235,231,218))
for i,role in enumerate(('HAB','GRN','PWR','TUB')):
 pic=p.render('GND_'+role,size=(600,340),theta=.10,elevation=.5,span=3.6,focus=(0,.90,0))
 x=i%2*600;y=65+i//2*365;im.paste(pic,(x,y+24));d.text((x+18,y),role+' / black sockets seated into hull',font=p.font(19),fill=(230,225,209))
im.save(R/'Previews/RoosterWorks-Ground-dev13-Roof-Sockets.jpg',quality=94)
print('Rendered native roof socket previews')
