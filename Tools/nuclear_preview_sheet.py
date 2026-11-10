from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',28)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
sheet=Image.new('RGB',(1500,560),(23,32,42));d=ImageDraw.Draw(sheet)
for i,(role,title,subtitle) in enumerate([('NST','Nuclear storage','Raw materials / fuel / depleted fuel'),('NSM','Nuclear smelter','Uraninite → RW feedstock'),('CEN','Fuel centrifuge','Feedstock → reactor fuel')]):
 im=Image.open(R/f'Previews/dev27-{role}.png').convert('RGB');im=im.resize((500,409),Image.Resampling.LANCZOS);sheet.paste(im,(i*500,80))
 d.text((i*500+22,18),role+'-250',font=font,fill=(235,191,93));d.text((i*500+22,51),title,font=small,fill='white')
 d.text((i*500+20,504),subtitle,font=small,fill=(205,215,224))
d.text((20,539),'ROOSTERWORKS  /  GROUND NUCLEAR INDUSTRY  /  dev.27 TEST — actual model previews',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14),fill=(162,178,192))
sheet.save(R/'Previews/dev27-NuclearFamily.png')
print('PASS assembled nuclear family preview')

