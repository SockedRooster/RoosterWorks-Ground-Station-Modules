import pathlib,zipfile,sys
import bpy
from mathutils import Vector
folder=pathlib.Path(__file__).resolve().parent
sdk=next((folder.parent/"Releases/2026-11-02").glob("*Modules*Source"))
helper=sdk/"Tools/create_gravity_blend.py"
ns={"__file__":str(helper)}
exec(compile(helper.read_text().split("scene=bpy.context.scene;scene.name=")[0],str(helper),"exec"),ns)
with zipfile.ZipFile(next(folder.glob("*dev.36-Install.zip"))) as z:
    for name in z.namelist():
        if name.endswith(".png") or name.endswith("RW_GND_HUB.mu"):
            z.extract(name,folder/"Build/Preview")
gd=folder/"Build/Preview/GameData/RoosterWorksGroundModules"
ns["GD"]=gd
scene=bpy.context.scene
ns["import_model"](gd/"Models/RW_GND_HUB.mu",scene)
for image in ns["images"].values(): image.alpha_mode="CHANNEL_PACKED"
for lamp_obj in scene.objects:
    if lamp_obj.type=="LIGHT": lamp_obj.hide_render=True
scene.render.engine="CYCLES";scene.cycles.samples=3;scene.cycles.use_denoising=True
scene.render.threads_mode="FIXED";scene.render.threads=1
scene.render.resolution_x=840;scene.render.resolution_y=620;scene.render.resolution_percentage=100
world=bpy.data.worlds.new("Studio");scene.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.18,.21,.25,1)
for coord,power,size in [((3,5,7),850,5),((-4,-3,3),600,4)]:
    lamp=bpy.data.lights.new("Softbox","AREA");obj=bpy.data.objects.new("Softbox",lamp);scene.collection.objects.link(obj);obj.location=coord;obj.rotation_euler=(-obj.location).to_track_quat("-Z","Y").to_euler();lamp.energy=power;lamp.size=size
cam=bpy.data.cameras.new("Camera");obj=bpy.data.objects.new("Camera",cam);scene.collection.objects.link(obj);scene.camera=obj;obj.location=(4,-7,5.3);obj.rotation_euler=(Vector((0,0,.15))-obj.location).to_track_quat("-Z","Y").to_euler()
cam.type="ORTHO";cam.ortho_scale=7.9
scene.render.filepath=str(folder/"Ground-Hub-dev36.png")
bpy.ops.render.render(write_still=True)




