"""Editable native hierarchy with collapsed/extended animation reference."""
from pathlib import Path
import sys,bpy,math
from mathutils import Matrix,Quaternion,Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Tools'))
from native_model import load
bpy.ops.wm.read_factory_settings(use_empty=True);model=load(R/'GameData/RoosterWorksGroundModules/Models/RW_GND_FLEX.mu')
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));materials=[];objects={}
for source in model.materials:
 m=bpy.data.materials.new(source['name']);m.use_nodes=True;shader=m.node_tree.nodes.get('Principled BSDF');n=m.node_tree.nodes.new('ShaderNodeTexImage');tex=model.textures[source['properties']['_MainTex']['index']]['name'];n.image=bpy.data.images.load(str(R/'GameData/RoosterWorksGroundModules/Models'/(tex+'.png')));n.image.pack();m.node_tree.links.new(n.outputs['Color'],shader.inputs['Base Color']);shader.inputs['Roughness'].default_value=.5;materials.append(m)
def recurse(n,parent=None):
 obj=bpy.data.objects.new(n['name'],None);bpy.context.scene.collection.objects.link(obj);objects[n['name']]=obj
 if parent:obj.parent=parent
 x,y,z,w=n['rotation'];native=Matrix.LocRotScale(Vector(n['position']),Quaternion((w,x,y,z)),Vector(n['scale']));obj.matrix_local=C@native@C.inverted()
 if 'mesh' in n:
  mesh=n['mesh'];data=bpy.data.meshes.new(n['name']+'_mesh');data.from_pydata([(x,-z,y) for x,y,z in mesh['vertices']],[],mesh['submeshes'][0]);data.update();uv=data.uv_layers.new(name='RW_UV')
  for face in data.polygons:
   for loop in face.loop_indices:uv.data[loop].uv=mesh['uvs'][data.loops[loop].vertex_index]
  geometry=bpy.data.objects.new(n['name']+'_geometry',data);bpy.context.scene.collection.objects.link(geometry);geometry.parent=obj;data.materials.append(materials[n['materials'][0]])
 if 'collider' in n:
  c=n['collider'];data=bpy.data.meshes.new(n['name']+'_collision');data.from_pydata([(x,-z,y) for x,y,z in c['mesh']['vertices']],[],c['mesh']['submeshes'][0]);data.update();geometry=bpy.data.objects.new(n['name']+'_collider',data);bpy.context.scene.collection.objects.link(geometry);geometry.parent=obj;geometry.display_type='WIRE';geometry.hide_render=True;geometry.hide_set(True)
 for child in n['children']:recurse(child,obj)
recurse(model.root);nose=objects['RW_TubeNose'];bellows=objects['RW_TubeBellows']
for frame,t in ((1,0),(121,1)):
 nose.location.x=.6+2.8*t;nose.keyframe_insert(data_path='location',frame=frame);bellows.scale.x=(.9+2.8*t)/.9;bellows.keyframe_insert(data_path='scale',frame=frame)
bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=121;bpy.context.scene.render.fps=20;bpy.context.scene.frame_set(1);bpy.context.scene.unit_settings.system='METRIC'
folder=R/'Source/Flex';folder.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RW_GND_FLEX.blend'));print('PASS saved editable FLEX rig with packed textures, nested contact hulls and 1.2/4.0 m animation reference')
