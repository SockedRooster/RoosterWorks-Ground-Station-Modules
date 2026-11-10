"""Native-equivalent compact hardpoint and actual VT mounting demonstration."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path[:0]=[str(R/'Tools'),str(R.parent/'rw-v075dev5/Tools')]
helper=R/'Tools/create_equipment_blend.py';source=helper.read_text().split('for i,path in enumerate(')[0]
source=source.replace("key=(src['name'],src['shader'])", "key=(src['name'],src['shader'],model.textures[src['properties']['_MainTex']['index']]['name'])")
exec(compile(source,str(helper),'exec'))
scene=bpy.context.scene;scene.name='RW_GND_HPT';scene.unit_settings.system='METRIC';import_model(GD/'Models/RW_GND_HPT.mu',scene)
demo=bpy.data.scenes.new('Side mount demonstration');bpy.context.window.scene=demo;import_model(GD/'Models/RW_GND_HPT.mu',demo)
for sign in (-1,1):
 before=set(demo.objects);import_model(GD/'Models/RW_GND_VT.mu',demo)
 root=next(o for o in demo.objects if o not in before and o.parent is None)
 root.location=(0,sign*1.25,0);root.rotation_euler.z=0 if sign>0 else math.pi
bpy.context.window.scene=scene
folder=R/'Source/Hardpoint';folder.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RW_GND_HPT.blend'));print('PASS packed native-equivalent hardpoint and mounting demonstration',flush=True)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,label,pos,target,scale in [('RW_GND_HPT','Collar',(4.5,6,3.1),(0,0,0),4.2),('RW_GND_HPT','FlatSide',(2.0,6,1.1),(0,.3,0),3.5),('Side mount demonstration','Mounted',(4.7,7,3.0),(0,0,0),6.0)]:
 scene=bpy.data.scenes[name];bpy.context.window.scene=scene
 for obj in list(scene.objects):
  if obj.name.startswith('Preview '):bpy.data.objects.remove(obj,do_unlink=True)
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview hardpoint '+label);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.22,.28,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.31));o=bpy.context.object;o.name='Preview floor';mat=bpy.data.materials.new('Preview concrete');mat.diffuse_color=(.18,.21,.24,1);o.data.materials.append(mat)
 for where,energy,size in [((-3,-4,6),1000,4),((3,4,4),650,4)]:
  data=bpy.data.lights.new('Preview light','AREA');o=bpy.data.objects.new('Preview light',data);scene.collection.objects.link(o);o.location=where;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
 data=bpy.data.cameras.new('Preview camera');o=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(o);scene.camera=o;data.type='ORTHO';data.ortho_scale=scale;o.location=pos;aim(o,target)
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev24-{label}.png');bpy.ops.render.render(write_still=True);print('PASS rendered hardpoint '+label,flush=True)
