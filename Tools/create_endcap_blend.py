"""Create an editable Blender source from the exact exported native meshes."""
import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'rw-v075dev5/Tools'))
from native_model import load,walk
bpy.ops.wm.read_factory_settings(use_empty=True)
path=R/'GameData/RoosterWorksGroundModules/Models/RW_GND_END_250_125.mu';model=load(path)
collection=bpy.data.collections.new('RW GROUND END-250-125 | MODEL ONLY');bpy.context.scene.collection.children.link(collection)
materials=[]
for source in model.materials:
 material=bpy.data.materials.new(source['name']);material.use_nodes=True;shader=material.node_tree.nodes.get('Principled BSDF');tex=material.node_tree.nodes.new('ShaderNodeTexImage');name=model.textures[source['properties']['_MainTex']['index']]['name'];tex.image=bpy.data.images.load(str(path.parent/(name+'.png')));tex.image.pack();material.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);shader.inputs['Roughness'].default_value=.45;materials.append(material)
for _,n in walk(model.root):
 if 'mesh' not in n:continue
 mesh=n['mesh'];data=bpy.data.meshes.new(n['name']);data.from_pydata([(x,-z,y) for x,y,z in mesh['vertices']],[],mesh['submeshes'][0]);data.update();uv=data.uv_layers.new(name='RW_UV')
 for face in data.polygons:
  for loop in face.loop_indices:uv.data[loop].uv=mesh['uvs'][data.loops[loop].vertex_index]
 obj=bpy.data.objects.new(n['name'],data);collection.objects.link(obj);data.materials.append(materials[n['materials'][0]])
for end,x in (('2.5 m structural attachment ONLY',-.45),('1.25 m docking',.45)):
 obj=bpy.data.objects.new(end,None);collection.objects.link(obj);obj.location=(x,0,0);obj.empty_display_type='ARROWS';obj.empty_display_size=.2
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Source/Endcap/RW_GND_END_250_125.blend'))
print('Saved editable endcap source with packed textures')
