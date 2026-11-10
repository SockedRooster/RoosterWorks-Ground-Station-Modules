"""Pack editable RoosterWorks-only geometry; render stock drill by local reference.

Stock drill meshes/textures are loaded only after saving the editable .blend.
The .blend never redistributes stock assets. Renders show the actual MODEL pose.
"""
from pathlib import Path
import sys,math
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path[:0]=[str(R/'Tools'),str(R.parent/'rw-v075dev5/Tools')]
helper=R/'Tools/create_equipment_blend.py'
source=helper.read_text().split('for i,path in enumerate(')[0]
source=source.replace("key=(src['name'],src['shader'])", "key=(src['name'],src['shader'],model.textures[src['properties']['_MainTex']['index']]['name'])")
exec(compile(source,str(helper),'exec'))

for i,path in enumerate(sorted((GD/'Models').glob('*.mu'))):
 scene=bpy.context.scene if i==0 else bpy.data.scenes.new(path.stem);scene.name=path.stem;scene.unit_settings.system='METRIC';import_model(path,scene)
bpy.context.window.scene=bpy.data.scenes['RW_GND_ISRU']
out=R/'Source/Industry/RoosterWorks-Ground-dev23.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));print('PASS packed editable RoosterWorks scenes; stock drill reference not embedded',flush=True)

from stock_drill_reader import load_stock
from industry_geometry import stock_pose
from native_model import walk
game=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/Squad/Parts/Resources/RadialDrill')
stock=load_stock(game/'TriBitDrill.mu')
def stock_material(src,model):
 key=('stock-drill',src['name'])
 if key in materials:return materials[key]
 mat=bpy.data.materials.new('Local Stock '+src['name']);mat.use_nodes=True
 shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.5
 prop=src['properties'].get('_MainTex')
 if prop:
  name=model.textures[prop['index']]['name'];path=game/(Path(name).stem+'.dds');im=bpy.data.images.load(str(path));im.pack()
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
 materials[key]=mat;return mat

for label,t in [('DrillRetracted',0),('DrillDeployed',1)]:
 scene=bpy.data.scenes.new('RW_GND_'+label);bpy.context.window.scene=scene
 import_model(GD/'Models/RW_GND_DRILL.mu',scene)
 oldmaterial=material;material=stock_material
 # Feed the already-read ephemeral model through the existing exact importer.
 posed=stock_pose(stock,t)
 for _,n in walk(posed.root):
  if 'mesh' in n and not n.get('materials'):del n['mesh']
 oldload=load;load=lambda _:posed
 import_model(game/'TriBitDrill.mu',scene);load=oldload;material=oldmaterial

def aim(obj,p):obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
views=[('RW_GND_ISRU','ISRU',(4,-7,3.1),(0,-.25,-.25),6.4,-2.32),('RW_GND_HAB','HullMounts',(4.8,5.5,2.8),(1.40,.62,.1),3.5,-2.32),('RW_GND_DrillRetracted','DrillRetracted',(3.4,5,2.1),(0,.45,0),4.6,-2.32),('RW_GND_DrillDeployed','DrillDeployed',(3.4,6,2.0),(0,.7,-.45),5.4,-2.32)]
for name,label,campos,target,zoom,floor in views:
 scene=bpy.data.scenes[name];bpy.context.window.scene=scene
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True
 scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Industry Preview '+label);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.23,.29,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floor));plane=bpy.context.object;plane.name='Preview ground';mat=bpy.data.materials.new('Preview concrete');mat.diffuse_color=(.18,.21,.24,1);plane.data.materials.append(mat)
 data=bpy.data.cameras.new('Preview camera');cam=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';cam.location=campos;data.ortho_scale=zoom;aim(cam,target)
 for pos,energy,size in [((-3,-4,6),1050,5),((4,3,4),650,4)]:
  data=bpy.data.lights.new('Preview fill','AREA');obj=bpy.data.objects.new('Preview fill',data);scene.collection.objects.link(obj);obj.location=pos;data.energy=energy;data.shape='DISK';data.size=size;aim(obj,target)
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev23-{label}.png');bpy.ops.render.render(write_still=True);print('PASS rendered industry '+label,flush=True)
