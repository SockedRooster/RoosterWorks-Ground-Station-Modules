"""Ground-only upper windows and level side plaques; core/art inputs stay read-only."""
import math,sys,types
# Blender doesn't bundle Pillow. These read-only procedural helpers reference
# it only in texture-generation functions; this exporter never calls those.
try:import PIL
except ImportError:
 pil=types.ModuleType('PIL')
 for name in ('Image','ImageDraw','ImageFont'):setattr(pil,name,types.ModuleType('PIL.'+name))
 sys.modules['PIL']=pil
from mathutils import Vector
import build_hab250 as h
import build_cmd250 as cmd
import build_lab250 as lab
import build_crew_tubes as tubes
from surface_uv import finish
from build_ring_options import components

def image_key(mat):
 images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat.use_nodes else []
 return images[0].name.rsplit('.',1)[0] if images else None

def label_removals(asset,deps,convert):
 regions=[];meshes=[]
 for obj in asset.objects:
  if obj.type!='MESH' or not (obj.name.startswith('Station heritage') or obj.name.startswith('Integrated observation')):continue
  ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
  points=[tuple(convert(obj.matrix_world@v.co)) for v in mesh.vertices]
  labels=[tuple(t.vertices) for t in mesh.loop_triangles if 'label' in (image_key(mesh.materials[t.material_index]) or '')]
  m={'vertices':points,'submeshes':[labels]}
  for group in components(m):
   pts=[points[i] for j in group for i in labels[j]]
   regions.append(([min(p[k] for p in pts)-.07 for k in range(3)],[max(p[k] for p in pts)+.07 for k in range(3)]))
  meshes.append((points,[tuple(t.vertices) for t in mesh.loop_triangles],[image_key(mesh.materials[t.material_index]) for t in mesh.loop_triangles]))
  ev.to_mesh_clear()
 remove=set()
 for pts,tris,mats in meshes:
  for material in set(mats):
   selected=[t for t,m in zip(tris,mats) if m==material];m={'vertices':pts,'submeshes':[selected]}
   for group in components(m):
    allpts=[pts[i] for j in group for i in selected[j]]
    inside=any(all(all(lo[k]<=p[k]<=hi[k] for k in range(3)) for p in allpts) for lo,hi in regions)
    if 'label' in (material or '') or (material in ('rwm_graphite','rwm_bronze','rwm_steel') and inside):
     remove.update(key([pts[i] for i in selected[j]]) for j in group)
 return remove

def key(points):return tuple(sorted(tuple(round(float(v),3) for v in p) for p in points))
def blank(extra=()):return {m:h.Mesh() for m in tuple(h.TEXTURES)+tuple(extra)}
def ground_point(p,A,C,translation,shift):return C@(A@Vector(p)+translation)-Vector((0,shift,0))
def windows(role,A,C,translation,shift):
 old=blank(('instrument',));new=[];fills=[]
 if role=='HAB':
  for row,col in sorted(h.BAYS):
   theta=math.tau*(col+1)/12;y=-1.730+(row+.5)*(3.460/8)
   h.panoramic_pressure_bay(old,theta,y,.710)
   fill=h.Mesh();h.flat_panel(fill,theta,y-.402,y+.402,1.49,1.204,segments=64);fills.append(fill)
  # Preserve six banks/eighteen panes, on the shoulders, clear of both roof heat exchangers.
  for phi in (48,132):
   for x in (-.98,0,.98):
    m=blank();h.panoramic_pressure_bay(m,0,0,.710)
    outline=h.curved_rect_contour(0,0,.733,.355*1.102,72,24);h.window_frame_ring(m['graphite'],outline,outline,1.165,1.2048)
    new.append((m,math.radians(phi),x,0,.65))
 elif role=='LAB':
  lab.lab_windows(old);m=blank(('instrument',));lab.lab_windows(m)
  outline=h.curved_rect_contour(0,.63,.53,.232,72,24);h.window_frame_ring(m['graphite'],outline,outline,1.165,1.209)
  new.append((m,math.radians(120),0,.63,1))
 elif role=='CMD':
  for theta in (-.90,-.45,0,.45,.90):cmd.command_window(old,theta,y=.171,hw=.143)
  for phi,x in ((60,-.20),(60,.20),(120,-.40),(120,0),(120,.40)):
   m=blank();cmd.command_window(m,0,y=0,hw=.143)
   outline=h.square_window_shape(0,0,.223,.223,radius=1.22,chamfer=.10);h.window_frame_ring(m['graphite'],outline,outline,1.165,1.219)
   new.append((m,math.radians(phi),x,0,.8))
 elif role=='AIR':
  # Remove the inherited orbital hatch hidden below the new dedicated ground door.
  h.hatch_pressure_bay(old,0,-.15,.92)
 remove={}
 for material,m in old.items():
  for tri in m.triangles:
   remove[key([ground_point(m.vertices[i],A,C,translation,shift) for i in tri])]=material
 additions=[]
 for m,phi,x,axial,scale in new:
  finish(m)
  for material,mesh in m.items():
   if not mesh.triangles:continue
   out=h.Mesh()
   for p,n in zip(mesh.vertices,mesh.normals):
    r=math.hypot(p[0],p[2])+.035;theta=math.atan2(p[0],p[2])*scale+phi
    out.vertices.append((x+(p[1]-axial)*scale,r*math.sin(theta),r*math.cos(theta)))
    # All viewports conform to the cylinder; rotate the original radial/axial normals.
    oldtheta=math.atan2(p[0],p[2]);radial=n[0]*math.sin(oldtheta)+n[2]*math.cos(oldtheta);tangent=n[0]*math.cos(oldtheta)-n[2]*math.sin(oldtheta)
    nn=Vector((n[1],radial*math.sin(theta)+tangent*math.cos(theta),radial*math.cos(theta)-tangent*math.sin(theta))).normalized();out.normals.append(tuple(nn))
   out.uvs=list(mesh.uvs);out.triangles=list(mesh.triangles);additions.append((material,out,'UpperWindows'))
 for fill in fills:
  out=h.Mesh();out.vertices=[tuple(ground_point(p,A,C,translation,shift)) for p in fill.vertices];out.normals=[tuple((C@A@Vector(n)).normalized()) for n in fill.normals];out.uvs=[(1-u,v) for u,v in fill.uvs];out.triangles=list(fill.triangles);additions.append(('cladding',out,'VacatedWindowShield'))
 return remove,additions

def plaque(role,texture):
 additions=[];radius=1.285 if role=='LOG' else 1.25;ycenter=1.48 if role=='HUB' else 0
 # The centered rear side stays clear of every ground door. Non-door barrels
 # receive a second plate on the opposite side. The elbow uses its outer curve.
 sides=(-1,1) if role=='LOG' else (-1,)
 if role=='ELB':sides=(1,)
 for side in sides:
  for material,width,height,r in (('graphite',.96,.44,radius),('bronze',.91,.40,radius+.007),(texture,.86,.36,radius+.013)):
   m=h.Mesh();rows=12;cols=12 if role=='ELB' else 1
   for j in range(rows):
    for k in range(cols):
     corners=((k/cols,j/rows),((k+1)/cols,j/rows),((k+1)/cols,(j+1)/rows),(k/cols,(j+1)/rows));pts=[];norms=[];uv=[]
     for u,v in corners:
      yy=(v-.5)*height;rr=math.sqrt(r*r-yy*yy)
      if role=='ELB':
       c,n,t,curvature=tubes.frame((.5-u)*width,True);p=(c[0]+rr*n[0],yy,-(c[1]+rr*n[1]));normal=(n[0]*rr/r,yy/r,-n[1]*rr/r)
      else:p=((u-.5)*width*(-side),yy+ycenter,side*rr);normal=(0,yy/r,side*rr/r)
      pts.append(p);norms.append(normal);uv.append((u,v))
     m.quad(pts,norms,uv)
   additions.append((material,m,'HorizontalSideLabel'))
 return additions
