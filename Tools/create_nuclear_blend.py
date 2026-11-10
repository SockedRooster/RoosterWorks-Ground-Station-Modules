"""Editable original MU-equivalent nuclear parts and exterior hardware previews."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path[:0]=[str(R/'Tools'),str(R.parent/'rw-v075dev5/Tools')]
helper=R/'Tools/create_equipment_blend.py';source=helper.read_text().split('for i,path in enumerate(')[0]
source=source.replace("key=(src['name'],src['shader'])", "key=(src['name'],src['shader'],model.textures[src['properties']['_MainTex']['index']]['name'])")
exec(compile(source,str(helper),'exec'))
for i,role in enumerate(('NST','NSM','CEN')):
 scene=bpy.context.scene if i==0 else bpy.data.scenes.new(role);scene.name='RW_GND_'+role;scene.unit_settings.system='METRIC'
 import_model(GD/('Models/RW_GND_'+role+'.mu'),scene)
folder=R/'Source/Nuclear';folder.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RoosterWorks-Ground-dev27.blend'))
print('PASS packed three original native-equivalent nuclear module scenes',flush=True)

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for role in ('NST','NSM','CEN'):
 scene=bpy.data.scenes['RW_GND_'+role];bpy.context.window.scene=scene
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
 scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview '+role);scene.world=world;world.use_nodes=True
 world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.22,.28,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-2.325));o=bpy.context.object;o.name='Preview floor'
 mat=bpy.data.materials.new('Preview concrete');mat.diffuse_color=(.18,.21,.24,1);o.data.materials.append(mat)
 target=(0,-.3,-.35)
 for where,energy,size in [((-3,-5,7),1600,4),((4,3,5),1000,4)]:
  data=bpy.data.lights.new('Preview light','AREA');o=bpy.data.objects.new('Preview light',data);scene.collection.objects.link(o);o.location=where;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
 data=bpy.data.cameras.new('Preview camera');o=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(o);scene.camera=o;data.type='ORTHO';data.ortho_scale=6.1;o.location=(4.8,-7,3.2);aim(o,target)
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev27-{role}.png');bpy.ops.render.render(write_still=True)
 print('PASS rendered nuclear module '+role,flush=True)
scene=bpy.data.scenes['RW_GND_NST'];bpy.context.window.scene=scene
scene.camera.location=(-4.8,7,3.2);aim(scene.camera,(0,.3,-.35))
scene.render.filepath=str(R/'Previews/dev27-NST-Opposite.png');bpy.ops.render.render(write_still=True)
print('PASS rendered opposite equipment flank',flush=True)

