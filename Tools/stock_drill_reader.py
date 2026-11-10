"""Read installed stock drill for diagnostics/previews, never export its assets.

Extends our strict native reader with animation records. Binary field layout
reference: https://github.com/taniwha/io_object_mu/blob/master/mu.py
The implementation below delegates all native geometry to our own reader.
"""
from pathlib import Path
import sys,inspect,textwrap
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parents[2];sys.path.insert(0,str(W/'rw-v075dev5/Tools'))
from native_model import Reader,walk

class StockReader(Reader):
 def particles(self):
  for fmt,count in [('B',1),('i',1),('f',10),('B',1),('f',4),('i',2),('f',12),('B',2),('f',34),('B',2),('f',3),('i',5)]:self.take(fmt,count)
 def skin(self,n):
  n['materials']=[self.take('i') for _ in range(self.take('i'))]
  self.take('f',6);self.take('i');self.take('B')
  n['bones']=[self.text() for _ in range(self.take('i'))]
  n['mesh']=self.mesh();n['shadows']=(1,1)
 def animation(self):
  clips=[]
  for _ in range(self.take('i')):
   clip={'name':self.text(),'bounds':self.take('f',6),'wrap':self.take('i'),'curves':[]}
   for _ in range(self.take('i')):
    path=self.text();prop=self.text();kind=self.take('i');wrap=self.take('i',2)
    count=wrap[1] if kind==8 else self.take('i')
    keys=[]
    for _ in range(count):keys.append((*self.take('f',4),self.take('i')))
    clip['curves'].append(dict(path=path,property=prop,kind=kind,keys=keys))
   clips.append(clip)
  return {'clips':clips,'default':self.text(),'autoplay':self.take('B')}

source=textwrap.dedent(inspect.getsource(Reader.node))
source=source.replace("elif tag==7:","elif tag==2:n['animation']=self.animation()\n        elif tag==7:")
source=source.replace("elif tag==7:","elif tag==9:self.skin(n)\n        elif tag==7:")
source=source.replace("elif tag==7:","elif tag==31:self.particles();n['particles']=True\n        elif tag==7:")
namespace={};exec(compile(source,'<extended-native-reader>','exec'),namespace);StockReader.node=namespace['node']
source=textwrap.dedent(inspect.getsource(Reader.mesh))
source=source.replace("elif tag==19:","elif tag==20:m['weights']=[[(self.take('i'),self.take('f')) for _ in range(4)] for _ in range(count)]\n        elif tag==21:m['bindposes']=[self.take('f',16) for _ in range(self.take('i'))]\n        elif tag==19:")
namespace={};exec(compile(source,'<extended-native-mesh-reader>','exec'),namespace);StockReader.mesh=namespace['mesh']

def load_stock(path):return StockReader(path).read()

if __name__=='__main__':
 m=load_stock('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/Squad/Parts/Resources/RadialDrill/TriBitDrill.mu')
 for p,n in walk(m.root):
  print(p,n['position'],n['rotation'],'vertices',len(n.get('mesh',{}).get('vertices',[])))
  if 'animation' in n:
   for clip in n['animation']['clips']:
    print('CLIP',clip['name'],len(clip['curves']))
    for c in clip['curves']:
     print('CURVE',c['path'],c['property'],'start',c['keys'][0][:2],'end',c['keys'][-1][:2])
