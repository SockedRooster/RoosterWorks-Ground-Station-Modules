from pathlib import Path
import sys,math,bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
helper=R/'Tools/create_equipment_blend.py';source=helper.read_text().split('for i,path in enumerate(')[0];exec(compile(source,str(helper),'exec'))
for label,path in [('Before',R.parent/'ground-hotpatch-v29/GameData/RoosterWorksGroundModules/Models/RW_GND_PWR.mu'),('After',GD/'Models/RW_GND_PWR.mu')]:
 scene=bpy.context.scene if label=='Before' else bpy.data.scenes.new(label);scene.name=label;scene.unit_settings.system='METRIC';import_model(path,scene)
folder=R/'Source/PowerSides';folder.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RW_GND_PWR-dev30.blend'));print('PASS packed exact before/after power modules',flush=True)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for label,pos in [('Before',(4.8,7,3.0)),('After',(4.8,7,3.0)),('Opposite',(-4.8,-7,3.0))]:
 scene=bpy.data.scenes['Before' if label=='Before' else 'After'];bpy.context.window.scene=scene
 for obj in list(scene.objects):
  if obj.name.startswith('Preview '):bpy.data.objects.remove(obj,do_unlink=True)
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True;scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview power '+label);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.20,.26,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-2.325));o=bpy.context.object;o.name='Preview floor';mat=bpy.data.materials.new('Preview concrete');mat.diffuse_color=(.18,.21,.24,1);o.data.materials.append(mat)
 for where,power,size in [((-3,-4,6),1100,4),((4,4,5),1000,4)]:
  data=bpy.data.lights.new('Preview light','AREA');o=bpy.data.objects.new('Preview light',data);scene.collection.objects.link(o);o.location=where;data.energy=power;data.size=size;aim(o,(0,0,-.4))
 data=bpy.data.cameras.new('Preview camera');o=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(o);scene.camera=o;data.type='ORTHO';data.ortho_scale=6.1;o.location=pos;aim(o,(0,0,-.4))
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev30-Power-{label}.png');bpy.ops.render.render(write_still=True);print('PASS rendered power '+label,flush=True)
