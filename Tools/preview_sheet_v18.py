from pathlib import Path
import sys
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Source'))
from appearance_textures import font
im=Image.new('RGB',(1500,1450),(16,24,31));d=ImageDraw.Draw(im)
d.text((28,18),'ROOSTERWORKS / GROUND dev.18',font=font(34,True),fill=(239,234,216))
d.text((28,65),'Door spotlights + integrated RCS + VT-60 vertical thrust pod',font=font(24),fill=(181,195,200))
for i,(role,title) in enumerate([('HAB','HAB / warm stair and landing light'),('CMD','COMMAND / independent exterior light'),('AIR','EVA / lit access stairs'),('VT','VT-60 / 60 kN / no docking ports')]):
 x=(i%2)*750;y=110+(i//2)*635;pic=Image.open(R/f'Previews/dev18-{role}.png').convert('RGB');pic.thumbnail((750,590));im.paste(pic,(x+(750-pic.width)//2,y+30));d.text((x+22,y),title,font=font(23,True),fill=(234,227,207))
d.text((28,1403),'Actual native geometry / illustrative Blender lighting / KSP testing pending',font=font(23),fill=(181,195,200));im.save(R/'Previews/RoosterWorks-Ground-dev18-Equipment.jpg',quality=94)
print('Saved equipment preview sheet')
