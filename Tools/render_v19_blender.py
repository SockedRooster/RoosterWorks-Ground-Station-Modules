"""Physical-light previews of shipped mesh scenes; Blender lighting is illustrative."""
from pathlib import Path
import bpy,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def aim(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
for role,night in [('HAB',True),('CMD',True),('AIR',True),('END_250_125',False),('VT',False)]:
 scene=bpy.data.scenes['RW_GND_'+role];bpy.context.window.scene=scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
 scene.render.resolution_x=900;scene.render.resolution_y=760;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 world=bpy.data.worlds.new('Preview sky '+role);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.13,.18,.23,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12 if night else .6
 floor=-1.35 if role=='END_250_125' else -2.31 if role!='VT' else -1.1
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floor));plane=bpy.context.object;plane.name='Preview ground only';mat=bpy.data.materials.new('Preview concrete '+role);mat.diffuse_color=(.20,.23,.25,1);plane.data.materials.append(mat)
 data=bpy.data.cameras.new('PreviewCamera');camera=bpy.data.objects.new('PreviewCamera',data);scene.collection.objects.link(camera);scene.camera=camera
 camera.location=(4.5,8,2.7) if role!='VT' else (3.2,5,1.9);aim(camera,(0,.7,-.48) if role!='VT' else (0,.65,.10));data.type='ORTHO';data.ortho_scale=6.1 if role=='HAB' else 5.5 if role not in ('VT','END_250_125') else 2.8
 if role=='END_250_125':camera.location=(-3.5,6,2);aim(camera,(0,0,0));data.ortho_scale=3.1
 light=bpy.data.lights.new('Preview fill','AREA');obj=bpy.data.objects.new('Preview fill',light);scene.collection.objects.link(obj);obj.location=(-3,4,6);aim(obj,(0,0,0));light.energy=60 if night else 800;light.shape='DISK';light.size=5
 # Native ground modules contain other interior lights; switch off those to
 # isolate the one actual door spot. Window material glow is a preview state.
 for obj in scene.objects:
  if obj.type=='LIGHT' and obj.data.type!='AREA' and not obj.name.startswith('RW_DoorSpot'):obj.data.energy=0
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(R/f'Previews/dev19-{role}.png');bpy.ops.render.render(write_still=True);print('PASS rendered',role,flush=True)
