from pathlib import Path
import sys,shutil
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'ground-hotpatch-v17'
# Keep an exact local build baseline in the source kit, so native additions
# can be rebuilt without requiring the separate older hot-patch directory.
baseline=R/'Source/BaselineDev17'
for relative in ('GameData/RoosterWorksGroundModules/Models','GameData/RoosterWorksGroundModules/Parts','Reports'):
 for p in (OLD/relative).glob('*'):
  if p.is_file() and (p.suffix in ('.mu','.cfg') or (p.suffix=='.json' and p.stem.startswith('RW_GND_'))):
   target=baseline/relative/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('v0.8.0-dev.17 TEST','v0.8.0-dev.18 TEST',1).replace('## Changes in dev.17','## Retained changes in dev.17',1)
intro='''## Changes in dev.18

- HAB, CMD and AIR/EVA now have a seated metal spotlight above the door. Its
  warm-white 90-degree beam points outward/down over the landing, stairs and
  ground, with a 9 m range. Use **Exterior Light On/Off**, or the stock Lights
  action group. It is independent of cabin/window controls and uses 0.03 EC/s.
- All twelve existing ground modules have four compact RCS clusters, two on
  the upper collar and two underneath: sixteen real nozzle transforms per
  part, 0.6 kN per active nozzle, stock monopropellant RCS and effects. Each
  part gains 0.04 t dry mass and 480 funds for this hardware. Existing fuel,
  electrical, science, crew and supply capacities are retained. Supply shared
  MonoPropellant from a connected VT-60 or another tank and enable vessel RCS.
  FLEX jets stay on its fixed rear collar, clear of the extending bellows.
- New **VT-60 Vertical Thrust Pod** is a surface/structural attachment with
  60 kN throttleable LFO thrust and a 3-degree gimbal. Fit balanced pairs on
  opposite sides, nozzles down and clear of doors, stairs and legs. It has no
  docking ports or command module. Dry mass 0.60 t; fully fueled mass 1.84 t;
  90 LiquidFuel, 110 Oxidizer and 60 MonoPropellant; 320 s vacuum / 260 s
  sea-level Isp. Each pod carries about 52 seconds of its own LFO at full
  vacuum thrust. It supplies the base's integrated RCS; no extra RCS jets are
  fitted to the thrust pod itself. Find it in **Engines** in the VAB/SPH.

Release the ground tether before using propulsion. Check the loaded center
of mass and thrust in the editor, then test low hops before a mission. A pair
provides 120 kN total; heavier bases may need more pods. This is a surface
handling/lift unit; the separate skycrane remains the orbital-delivery build.
No automatic landing or guaranteed orbit-to-surface capability is implied.

Close KSP, replace **GameData/RoosterWorksGroundModules** with this package's
folder, and restart. Keep RoosterWorks Station Modules installed. This remains
a ground add-on update; it does not replace the station, support or skycrane
folders. All 25 existing ground docking ports, docking pull, EVA interlocks,
deployment animation, window/badge refinements and Kerbalism patches remain.

Offline validation covers all 13 native models, every original model node,
all 192 RCS nozzle axes, all eight stair treads in each spotlight cone, five
stair poses around the fixtures, engine/gimbal axes, fuels, original resource
balance and unchanged read-only inputs. Runtime compilation uses installed
KSP 1.12.5 assemblies. Docking, FLEX/window and exterior-menu suites total
5,197 assertions. These checks do not replace in-game lighting, RCS, flight,
heat, save/reload and low-EC testing; those remain pending.

**Current source:** Source/Equipment/RoosterWorks-Ground-dev18.blend contains
all thirteen current native-model scenes, packed textures and actual light
directions. Tools/build_v18.py builds the new geometry/configs from the exact
Source/BaselineDev17 snapshot; it also requires the Station Modules developer
source helpers in the adjacent rw-v075dev5 directory. Earlier Source/Endcap,
Source/Flex and older tools are retained historical sources, not the current
full equipment scenes. Do not run earlier stage/finalizer tools over dev.18.

Rebuild current content with Tools/build_v18.py, Tools/build-runtime.ps1 and
Tools/refresh_manifest.py. Then run Tools/validate.py, Tools/validate_v18.py,
Tools/test-docking.ps1, Tools/test-flex.ps1 and Tools/test-exterior.ps1. Use
Tools/create_equipment_blend.py in Blender for editable scene regeneration.
Previews show exact model geometry with illustrative Blender lighting;
brightness and shadows must still be checked in KSP.

'''
s=s.replace('## Retained changes in dev.17',intro+'## Retained changes in dev.17',1);p.write_text(s,encoding='utf-8')
p=R/'ROADMAP.md';s=p.read_text(encoding='utf-8');s+='''

## Ground implementation candidate — dev.18 / 2026-10-15

The ground portion of the RCS, exterior-lighting and propulsion work is now
built for testing: top/bottom RCS on all twelve base modules, warm door
spotlights on HAB/CMD/EVA and a separate VT-60 vertical-lift pod. Orbital
station equivalents and exterior lights for other ground roles remain future
work. In-game validation is pending; this does not establish release status.
''';p.write_text(s,encoding='utf-8')
(R/'Source/Equipment/README.md').write_text('''# Current dev.18 editable source

RoosterWorks-Ground-dev18.blend has one scene per shipped part, preserving the
native transform hierarchy, meshes, UVs, texture materials and light frames.
The coordinate conversion reflects Unity X/Y/Z to Blender X/Z/Y and reverses
triangle winding. In particular, Unity spotlights emit local +Z; their Blender
children rotate to emit along the corresponding converted axis. Blender energy
and window emission are illustrative, not a conversion of KSP photometry.

Tools/build_v18.py is the canonical procedural equipment/VT builder. All prior
mechanical rigs/colliders are read unchanged from Source/BaselineDev17. Runtime
leg/stair and FLEX animations remain implemented by their existing C# modules
and CFG transforms; the current full Blender scenes are editable pose snapshots.
''',encoding='utf-8')
print('Updated dev.18 install, fuel/operation, source and roadmap notes; bundled protected native baseline')
