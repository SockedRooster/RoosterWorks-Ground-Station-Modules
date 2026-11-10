"""Pack the owned colored frames, then preview assembled stock mechanisms.

Stock assets are referenced from installed KSP only, after the .blend save.
"""
from pathlib import Path
import sys,math,copy,json,bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path[:0]=[str(R/'Tools'),str(R.parent/'rw-v075dev5/Tools'),str(R.parent/'rw-v075dev5/Source')]
helper=R/'Tools/create_equipment_blend.py';source=helper.read_text().split('for i,path in enumerate(')[0]
source=source.replace("key=(src['name'],src['shader'])", "key=(src['name'],src['shader'],model.textures[src['properties']['_MainTex']['index']]['name'])")
exec(compile(source,str(helper),'exec'))
from config_nodes import parse
from stock_drill_reader import load_stock
from industry_geometry import stock_pose
from native_model import walk
specs=[json.loads((R/'Reports/DEV31_WATER_DRILL.json').read_text())];base=load(GD/'Models/RW_GND_DRILL.mu');oldload=load
for i,spec in enumerate(specs):
 scene=bpy.context.scene if i==0 else bpy.data.scenes.new(spec['id']);scene.name=spec['id'];bpy.context.window.scene=scene;scene.unit_settings.system='METRIC'
 p=parse((GD/f"Parts/{spec['id']}.cfg").read_text()).children[0];frame=next(n for n in p.children if n.header=='MODEL' and n.get('model').startswith('RoosterWorks'))
 remaps={v.split(',')[0].strip():v.split(',')[1].strip().split('/')[-1] for k,v in frame.values if k=='texture'}
 m=copy.deepcopy(base)
 for t in m.textures:
  if t['name'] in remaps:t['name']=remaps[t['name']]
 load=lambda _:m;import_model(GD/'Models/RW_GND_DRILL.mu',scene);load=oldload
 scene['ResourceName']=spec['resource'];scene['BufferLiters']=spec['buffer_liters'];scene['StockMechanismReference']='Squad/Parts/Resources/RadialDrill/TriBitDrill';scene['StockMechanismScale']=.5
bpy.context.window.scene=bpy.data.scenes[specs[0]['id']]
folder=R/'Source/WaterDrill';bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RW_WaterDrillFrame.blend'));print('PASS packed editable water drill frame; stock assets not embedded',flush=True)

game=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/Squad/Parts/Resources/RadialDrill');stock=stock_pose(load_stock(game/'TriBitDrill.mu'),0)
for _,n in walk(stock.root):
 if 'mesh' in n and not n.get('materials'):del n['mesh']
def stock_material(src,model):
 key=('stock-drill',src['name'])
 if key in materials:return materials[key]
 mat=bpy.data.materials.new('Local Stock '+src['name']);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.5
 prop=src['properties'].get('_MainTex')
 if prop:
  name=model.textures[prop['index']]['name'];im=bpy.data.images.load(str(game/(Path(name).stem+'.dds')));im.pack();tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
 materials[key]=mat;return mat
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for spec in specs:
 scene=bpy.data.scenes[spec['id']];bpy.context.window.scene=scene
 oldmaterial=material;material=stock_material;load=lambda _:stock;import_model(game/'TriBitDrill.mu',scene);load=oldload;material=oldmaterial
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True;scene.render.resolution_x=650;scene.render.resolution_y=760;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview '+spec['code']);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.23,.28,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.85));o=bpy.context.object;o.name='Preview floor';mat=bpy.data.materials.new('Preview concrete');mat.diffuse_color=(.18,.21,.24,1);o.data.materials.append(mat)
 for pos,energy,size in [((-2,3,4),800,4),((3,-2,3),600,3)]:
  data=bpy.data.lights.new('Preview light','AREA');o=bpy.data.objects.new('Preview light',data);scene.collection.objects.link(o);o.location=pos;data.energy=energy;data.shape='DISK';data.size=size;aim(o,(0,.35,0))
 data=bpy.data.cameras.new('Preview camera');o=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(o);scene.camera=o;data.type='ORTHO';data.ortho_scale=2.25;o.location=(2.1,4,1.4);aim(o,(0,.35,0))
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f"Previews/dev31-Drill-{spec['code']}.png");bpy.ops.render.render(write_still=True);print('PASS rendered specialist '+spec['resource'],flush=True)
