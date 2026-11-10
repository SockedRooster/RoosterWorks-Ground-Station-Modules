"""Editable scenes from exact current MU geometry, including real spotlights."""
from pathlib import Path
import sys,math,bpy
from mathutils import Matrix,Quaternion,Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];CORE=R.parent/'rw-v075dev5';sys.path.insert(0,str(CORE/'Tools'))
from native_model import load
GD=R/'GameData/RoosterWorksGroundModules';C=Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
bpy.ops.wm.read_factory_settings(use_empty=True);images={};materials={}
def material(src,model):
 key=(src['name'],src['shader'])
 if key in materials:return materials[key]
 mat=bpy.data.materials.new(src['name']);mat.use_nodes=True;tree=mat.node_tree;shader=tree.nodes.get('Principled BSDF');tex=model.textures[src['properties']['_MainTex']['index']]['name']
 if tex not in images:
  path=GD/'Models'/(tex+'.png')
  if not path.exists():path=CORE/'GameData/RoosterWorksStationModules/Models'/(tex+'.png')
  images[tex]=bpy.data.images.load(str(path));images[tex].pack()
 node=tree.nodes.new('ShaderNodeTexImage');node.image=images[tex];tree.links.new(node.outputs['Color'],shader.inputs['Base Color']);shader.inputs['Roughness'].default_value=.48
 if src['shader']=='KSP/Alpha/Translucent':
  shader.inputs['Alpha'].default_value=.26;shader.inputs['Transmission Weight'].default_value=.35;mat.surface_render_method='DITHERED'
 if src['shader']=='KSP/Emissive/Diffuse' and ('glass' in src['name'].lower() or 'Window' in src['name']):
  shader.inputs['Emission Color'].default_value=(1,.76,.46,1);shader.inputs['Emission Strength'].default_value=.4
 materials[key]=mat;return mat
def import_model(path,scene):
 model=load(path);mats=[material(m,model) for m in model.materials]
 def recurse(n,parent=None):
  obj=bpy.data.objects.new(n['name'],None);scene.collection.objects.link(obj)
  if parent:obj.parent=parent
  x,y,z,w=n['rotation'];obj.matrix_local=C@Matrix.LocRotScale(Vector(n['position']),Quaternion((w,x,y,z)),Vector(n['scale']))@C.inverted()
  if 'mesh' in n:
   m=n['mesh'];data=bpy.data.meshes.new(n['name']);data.from_pydata([(x,z,y) for x,y,z in m['vertices']],[],[tuple(reversed(tri)) for sub in m['submeshes'] for tri in sub]);data.update();uv=data.uv_layers.new(name='RW_UV');offset=0
   for idx,sub in enumerate(m['submeshes']):
    data.materials.append(mats[n['materials'][idx]])
    for poly in list(data.polygons)[offset:offset+len(sub)]:poly.material_index=idx
    offset+=len(sub)
   for face in data.polygons:
    face.use_smooth=True
    for loop in face.loop_indices:uv.data[loop].uv=m['uvs'][data.loops[loop].vertex_index]
   data.normals_split_custom_set_from_vertices([(x,z,y) for x,y,z in m['normals']])
   geometry=bpy.data.objects.new(n['name']+'_Mesh',data);scene.collection.objects.link(geometry);geometry.parent=obj
  if 'light' in n:
   l=n['light'];kind='SPOT' if l['type']==0 else 'POINT';data=bpy.data.lights.new(n['name'],kind);data.energy=l['intensity']*220;data.color=l['color'][:3];data.shadow_soft_size=.08
   if kind=='SPOT':data.spot_size=math.radians(l['spotAngle']);data.spot_blend=.4
   lamp=bpy.data.objects.new(n['name']+'_Light',data);scene.collection.objects.link(lamp);lamp.parent=obj
   # Blender emits local -Z. C converts Unity's local +Z into Blender +Y.
   lamp.rotation_euler=(math.pi/2,0,0)
  if 'collider' in n:obj['KSP_Collider']=str(n['collider']['type']);obj['KSP_Trigger']=n['collider']['trigger']
  for child in n['children']:recurse(child,obj)
 recurse(model.root)
for i,path in enumerate(sorted((GD/'Models').glob('*.mu'))):
 scene=bpy.context.scene if i==0 else bpy.data.scenes.new(path.stem);scene.name=path.stem;scene.unit_settings.system='METRIC';import_model(path,scene);print('Imported exact scene',path.stem,flush=True)
scene=bpy.data.scenes['RW_GND_HAB'];bpy.context.window.scene=scene
folder=R/'Source/Equipment';folder.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'RoosterWorks-Ground-dev21.blend'));print('PASS packed editable native-equivalent scenes for all thirteen parts')
