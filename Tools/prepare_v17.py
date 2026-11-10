from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Tools/package.py';s=p.read_text().replace('v0.8.0-dev.16','v0.8.0-dev.17').replace("endswith('.mu')])==11","endswith('.mu')])==12").replace('eleven models','twelve models');p.write_text(s)
p=R/'Tools/build_configs.py';p.write_text(p.read_text().replace("'BUILD':16","'BUILD':17"))
p=R/'Tools/validate.py';s=p.read_text().replace("glob('*.cfg')))==11","glob('*.cfg')))==12").replace("==ids|{'RW_GND_END_250_125'}","==ids|{'RW_GND_END_250_125','RW_GND_FLEX'}")
s=s.replace("for path in (GD/'Compatibility').glob('*.cfg'):","for path in (GD/'Compatibility').glob('*.cfg'):\n    if path.name=='FlexRingGeometry.cfg':continue # Dedicated flex validation handles moving parents and legless hull.")
p.write_text(s)
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('v0.8.0-dev.16 TEST','v0.8.0-dev.17 TEST',1).replace('## Changes in dev.16','## Retained changes in dev.16',1)
intro='''## Changes in dev.17

Every connection-end rooster is now a separate upright outward-readable badge
above the small porthole, including the structural rear of the rounded endcap.
The side/body rooster artwork on HAB, AIR/EVA and CMD rotates 90 degrees clockwise;
the end badges use their own world-up UV mapping. Existing text plates stay intact.

All end portholes now have warm-white emissive glass. On crewed modules and the
hub they follow the existing cabin-light switch. On GRN they follow inspection
lights, independently of grow lamps. Other modules gain a Module Lights control.
These are luminous window surfaces, not new exterior spotlights. All prior
greenhouse and cabin lighting remains. Acquire force doubles from 20 to 40;
the 2.5 m range, 75-degree initial acceptance, alignment torque 30, final seating
criteria and manual-release naming remain from dev.16. Release ground tethers
while repositioning modules.

### New FLEX collapsible crew tube

RW_GND_FLEX is a legless 2.5 m connector with stock size2 docking on both ends.
It has a 1.2 m collapsed length and 4.0 m fully extended length, with a 6-second
accordion animation and persistent intermediate lengths. Fixed rear is End B;
the moving nose is End A. Attach the rear to the base, extend the free nose,
then dock the receiving module. Extension and collapse are available in the
editor and flight while the moving end is free. A connected/acquiring nose
locks length, including if capture begins during movement; existing joints
are never intentionally stretched or other parts teleported. Motion pauses
while packed, unloaded or in time warp. The port frame, visual hull and pressure
collider share the moving/scale parents and attachment-node positions.

The tube has White/Grey finish, ring colors and end-window lights. It is a
crewless passage (0.65 t / 4600 funds), with optional Connected Living Space
passability. It adds no seats, storage or habitable volume: existing Kerbalism
habitats retain the base's life-support capacity. It has no legs, stairs or EVA
hatch. No new fuel, RCS or exterior spotlight functionality is added here.

Close KSP, replace GameData/RoosterWorksGroundModules and restart. The endcap
still has only its 1.25 m docking port; its 2.5 m rear is structural. Earlier
rear-port saved-craft guidance remains applicable. Existing resource balance,
models' hull/contact collision and deployment/tether behavior are preserved.
Confirm light switching, badge orientation, magnetic handling and FLEX capture,
release and save/reload in game; offline tests do not simulate KSP/PhysX.

Native inspection previews are in Previews/RoosterWorks-Ground-dev17-Lights.jpg
and Previews/RoosterWorks-Ground-dev17-Flex.jpg. Window glow is an approximation
of the new emissive shader; these are native model renders, not concept art.

Rebuild order: Tools/end_face_refinements.py (reads protected dev.16 models),
Tools/build_flex_tube.py, Tools/finalize_v17.py, Tools/build-runtime.ps1, then
Tools/refresh_manifest.py. Run Tools/test-docking.ps1, Tools/test-flex.ps1,
Tools/validate.py and Tools/validate_v17.py before packaging. Rebuild the editable
FLEX Blender rig with Tools/create_flex_blend.py and the updated endcap source
with Tools/create_endcap_blend.py. Earlier stage tools describe their historical
scopes; the dev.17 suite is authoritative for this update.

'''
s=s.replace('## Retained changes in dev.16',intro+'## Retained changes in dev.16',1);p.write_text(s,encoding='utf-8')
print('Prepared dev.17 documentation and twelve-model package scope')
