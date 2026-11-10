from pathlib import Path
import shutil,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'ground-hotpatch-v18';baseline=R/'Source/BaselineDev18'
for rel in ('GameData/RoosterWorksGroundModules/Models','GameData/RoosterWorksGroundModules/Parts','Reports'):
 for p in (OLD/rel).glob('*'):
  if p.is_file() and (p.suffix in ('.mu','.cfg') or (p.suffix=='.json' and p.stem.startswith('RW_GND_'))):
   dest=baseline/rel/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
p=R/'Tools/create_equipment_blend.py';s=p.read_text().replace('RoosterWorks-Ground-dev18.blend','RoosterWorks-Ground-dev19.blend');p.write_text(s)
p=R/'Tools/render_v18_blender.py';s=p.read_text().replace("[('HAB',True),('CMD',True),('AIR',True),('VT',False)]","[('HAB',True),('CMD',True),('AIR',True),('END_250_125',False),('VT',False)]").replace("f'Previews/dev18-","f'Previews/dev19-")
s=s.replace("floor=-2.31 if role!='VT' else -1.1","floor=-1.35 if role=='END_250_125' else -2.31 if role!='VT' else -1.1")
s=s.replace("camera.location=(4.5,8,2.7)","camera.location=(4.5,8,2.7)")
s=s.replace("data.ortho_scale=6.1 if role=='HAB' else 5.5 if role!='VT' else 2.8","data.ortho_scale=6.1 if role=='HAB' else 5.5 if role not in ('VT','END_250_125') else 2.8\n if role=='END_250_125':camera.location=(-3.5,6,2);aim(camera,(0,0,0));data.ortho_scale=3.1")
(R/'Tools/render_v19_blender.py').write_text(s)
p=R/'Tools/preview_sheet_v18.py';s=p.read_text().replace('dev.18','dev.19').replace('integrated RCS + VT-60','no RCS + VT-90').replace("('AIR','EVA / lit access stairs')","('END_250_125','ENDCAP / turned end-for-end')").replace('VT-60 / 60 kN / no docking ports','VT-90 / 90 kN / complete pod release').replace('dev18-','dev19-');(R/'Tools/preview_sheet_v19.py').write_text(s)
readme='''# RoosterWorks Ground Modules — v0.8.0-dev.19 TEST

Requires KSP 1.12.5, ModuleManager and RoosterWorks Station Modules v0.7.5-dev.5.
Kerbalism and the existing optional integrations remain supported. This is a
local test build, not a published release. The installed game/saves were read
for diagnosis only and have not been modified.

## Changes

- Door lights on HAB, CMD and AIR/EVA now explicitly control real Unity
  spotlights: downward/outward, 100-degree cone, 10 m range, forced pixel
  rendering and no fixture self-shadowing. They follow the cabin-light switch
  by default. Exterior Light On/Off makes an independent persistent override;
  Link Exterior to Cabin Lights restores following. Lights action group is
  supported. Actual light and lens go dark without power; 0.03 EC/s per lamp.
- HAB side rooster symbols rotate 180 degrees from dev.18. Existing text
  plaques and separate upright end-face badges retain their mapping.
- FLEX Extend Crew Tube and Collapse Crew Tube remain visible in editor and
  flight, including when connected. If its moving end is connected/acquiring,
  clicking explains the lock rather than hiding both controls or stretching
  joints. Model/port binding retries after initialization. Fixed rear remains
  attached; undock the moving nose before resizing. Length remains 1.2–4 m.
- The rounded 2.5-to-1.25 endcap turns end-for-end by 180 degrees about its
  upright axis. Model, collision, stack-node directions and small docking frame
  turn together. Large end stays structural only; small end remains size1 dock.
- RCS removed completely from all ground module models/configs/effects. The
  0.04 t / 480 funds added to the twelve existing modules for RCS is removed.
- VT-60's existing part ID becomes the **VT-90 Detachable Vertical Thrust Pod**:
  90 kN thrust (+50%), 180 LiquidFuel and 220 Oxidizer (double), no
  MonoPropellant. Dry mass 0.60 t, full mass 2.60 t, Isp 320 s vacuum / 260 s
  sea level, gimbal 3 degrees. Fit balanced pairs with nozzles down. No ports.
- **Decouple Thrust Pod** shuts down its engine and invokes a stock whole-part
  decoupler, ejecting the entire pod/bracket outward. It leaves no anchored
  baseplate behind. Manual flight button/action; not tied to staging. Pod is
  surface-attach only so the release always uses the correct mounting joint.

## Install and test

Close KSP, replace only GameData/RoosterWorksGroundModules, then restart. Keep
the core Station Modules folder. No Station Support or skycrane replacement
is required. Try newly placed endcaps/pods in a test craft: the endcap's native
node orientation changed and the pod now has a surface decoupler. No existing
save/craft was rewritten. Release the ground tether before using propulsion.

Check cabin-light illumination on the stairs/terrain, exterior override/off,
low-EC recovery, FLEX controls with free and attached ends, endcap attachment,
and pod separation with the engine running. Ground illumination, capture,
separation and flight behavior still require confirmation in the actual game.
Offline checks cannot reproduce the installed rendering or PhysX behavior.

## Source and checks

Current source is Source/Equipment/RoosterWorks-Ground-dev19.blend, all thirteen
native scenes with packed textures. Tools/build_v19.py is the authoritative
geometry/config builder; Source/BaselineDev18 is its read-only reference
snapshot. It requires the adjacent rw-v075dev5 Station developer helpers.
Earlier builders, baselines and Blender files are historical references.

Build: Tools/build_v19.py; Tools/build-runtime.ps1; Tools/refresh_manifest.py.
Validate: Tools/validate.py; Tools/validate_v19.py; Tools/test-docking.ps1;
Tools/test-flex.ps1; Tools/test-light-release.ps1. Runtime compiles against
installed KSP 1.12.5 assemblies. Tests exercise actual controller sources with
test doubles: docking/menu, visible FLEX controls, real light enable/power
states and engine shutdown before stock pod release. Native tests cover
zero RCS, preserved resources, badges, all eight treads per beam, rotated
endcap geometry/collisions/interfaces, pod fuels/thrust and archive integrity.
Previews use exact native geometry with illustrative Blender lighting.
'''
(R/'README.md').write_text(readme,encoding='utf-8')
(R/'Source/Equipment/README.md').write_text('''# Current dev.19 source

RoosterWorks-Ground-dev19.blend contains all thirteen current native mesh
scenes. Unity X/Y/Z maps to Blender X/Z/Y with reversed triangle winding.
Unity lights emit local +Z; their Blender child lamp frames account for that
basis. Blender light wattage/emission is illustrative. The actual game light
controller is Source/ExteriorLight.cs, including ForcePixel, EC and cabin link.
Leg/stair/FLEX motion remains driven by the C# modules and CFG transforms;
these editable scenes are pose snapshots. Tools/build_v19.py is canonical.
Older scene files/builders are retained as historical references.
''',encoding='utf-8')
with (R/'ROADMAP.md').open('a',encoding='utf-8') as f:f.write('''

## Ground dev.19 correction

Integrated RCS is withdrawn at user request from all ground modules. Door
spotlight control and FLEX controls are revised for testing. VT-90 lift pod
replaces VT-60 statistics and gains clean whole-pod separation. Live KSP
confirmation remains pending; orbital station changes remain future work.
''')
print('Prepared dev.19 source baseline, source/preview tools, install and operation notes')
