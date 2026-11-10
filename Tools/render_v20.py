from pathlib import Path
import bpy,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def aim(obj,p):obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
views=[('CMD','Command',None),('CMD','Dish',None),('LAB','ScienceLight',None),('FLEX','TubeCollapsed',0),('FLEX','TubeExtended',1)]
import sys
if '--command-only' in sys.argv:views=views[:1]
for role,label,t in views:
 scene=bpy.data.scenes['RW_GND_'+role];bpy.context.window.scene=scene
 for obj in list(scene.objects):
  if obj.name.startswith('Preview '):bpy.data.objects.remove(obj,do_unlink=True)
 if role=='FLEX':scene.objects['RW_TubeNose'].location.x=.6+2.8*t;scene.objects['RW_TubeBellows'].scale.x=(.9+2.8*t)/.9
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview world '+label);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.17,.22,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12 if role=='LAB' else .55
 floor=-2.31 if role in ('CMD','LAB') else -1.30
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floor));plane=bpy.context.object;plane.name='Preview floor '+label;mat=bpy.data.materials.new('Preview concrete '+label);mat.diffuse_color=(.18,.21,.24,1);plane.data.materials.append(mat)
 data=bpy.data.cameras.new('Preview camera '+label);cam=bpy.data.objects.new('Preview camera '+label,data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
 cam.location=(4.5,8,3);aim(cam,(0,.7,0));data.ortho_scale=6.7
 if label=='Dish':cam.location=(3,5,3.3);aim(cam,(.375,.12,1.85));data.ortho_scale=1.35
 if role=='FLEX':cam.location=(5.5+1.4*t,8,3.2);aim(cam,(1.4*t,0,0));data.ortho_scale=5.3 if t else 3.2
 light=bpy.data.lights.new('Preview fill '+label,'AREA');ob=bpy.data.objects.new('Preview fill '+label,light);scene.collection.objects.link(ob);ob.location=(-3,4,6);aim(ob,(0,0,0));light.energy=60 if role=='LAB' else 800;light.shape='DISK';light.size=5
 for obj in scene.objects:
  if obj.type=='LIGHT' and obj.data.type!='AREA' and not obj.name.startswith('RW_DoorSpot'):obj.data.energy=0
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev20-{label}.png');bpy.ops.render.render(write_still=True);print('PASS rendered',label,flush=True)
