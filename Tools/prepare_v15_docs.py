from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Tools/package.py';p.write_text(p.read_text().replace('v0.8.0-dev.14','v0.8.0-dev.15'))
p=R/'Tools/build_configs.py';p.write_text(p.read_text().replace("'BUILD':14","'BUILD':15"))
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('v0.8.0-dev.14 TEST','v0.8.0-dev.15 TEST',1).replace('## Changes in dev.14','## Retained changes in dev.14',1)
intro='''## Changes in dev.15

- Endcap: one 1.25 m docking port at the small end. The large 2.5 m end
  retains its structural stack attachment, with no docking module/transform.
  The small face uses new clean layered hatch geometry and continuous planar
  UVs, replacing the compressed blanket. The nose rooster orientation is corrected; the accepted rear crest is retained.
- PWR: the nameplate, bronze rim and black backing move together down the
  cylinder by 35 degrees (about 0.72 m at the plate center), clearing equipment.
- ELB: rooster-symbol UVs rotate 270 degrees clockwise; text plates stay intact.
- Docking menus: only ground CMD's command module retains Control From Here.
  Docking-port reference controls, port names, rename buttons and acquire/capture
  force fields are hidden. Optional NavyFish/DPAI naming data and targeting
  remain intact; the plugin is not removed or required by this addon.
- Manual release buttons read Undock(Connected part title), including ports
  pre-attached in the editor. Labels refresh after connection or title changes.
  Targeting and the stock docking/release state machines remain active.
- Ground ports attract within 2.5 m using acquireForce 20 and acquireTorque 12
  (stock defaults 2 and 2). Forward alignment must be within about 11.5 degrees;
  capture is within 0.08 m / about 3.6 degrees and retains the stock 0.3 m/s
  maximum relative capture speed. Force percentage is locked to 100. After
  undocking, separate beyond 3 m before recapture is possible. These are initial
  tuning values requiring in-game confirmation; tethered feet still resist motion.
- Roadmap adds top/bottom RCS thrusters, exterior lighting and dedicated thruster
  modules. No milestone/version has been invented for these future items.

Compatibility: an optional, narrowly scoped rule matches SC Carrier END_250_125
to the sole size1 endcap port if RoosterWorksSkycrane is installed. No skycrane
source, model or existing addon file is overwritten. Its rigid pickup remains
at the small end. Capture tuning is applied only to RW.GND./RW_GND_ ground IDs.

Close KSP, replace GameData/RoosterWorksGroundModules and restart. Existing craft
that used the endcap's removed rear docking interface need review; replace that
endcap in the editor for new test craft. Removing a docking module can leave
old saved docking metadata referring to the former port. No saves are edited.

Native preview: Previews/RoosterWorks-Ground-dev15-Artwork.jpg. Offline checks
cover menu reloads, command retention, DPAI controls, connected-part labels,
stock API compilation, model geometry and preservation scope. They do not
replace in-game visual, attraction, release and saved-craft testing.

Rebuild the endcap with Tools/build_endcap.py. Apply Tools/refine_badges.py
against the protected accepted dev.14 PWR/ELB models, then compile the runtime
with Tools/build-runtime.ps1 and run Tools/finalize_v15.py last. Refresh the
endcap Blender scene with Tools/create_endcap_blend.py. Validate with
Tools/validate.py, Tools/validate_v15.py and Tools/test-docking.ps1. The tether
and deployment source code are unchanged; their regression tools are retained.

'''
s=s.replace('## Retained changes in dev.14',intro+'## Retained changes in dev.14',1);p.write_text(s,encoding='utf-8')
roadmap=(R.parent/'rw-v075dev5/ROADMAP.md').read_text(encoding='utf-8')
roadmap=roadmap.replace('Current candidate: **0.75 / v0.7.5-dev.5**, extending the accepted 0.6.0 source kit. All prior features and development history remain retained. Live KSP acceptance of the new controls is pending.','Station source baseline: v0.7.5-dev.5. Ground integration candidate: v0.8.0-dev.15. Earlier milestone descriptions below retain their development history; no publication/release status is implied.')
roadmap+='''
## Added future work — 2026-10-15

- Top and bottom RCS thrusters for station/ground-module handling.
- Exterior module lighting.
- Dedicated thruster modules.

Milestone assignment, thrust, fuels, attachment layout and lighting controls
remain to be designed. These are roadmap items, not parts shipped in dev.15.
The separate SC-250 skycrane v0.1.0-dev.1 remains a local transport test build.
'''
(R/'ROADMAP.md').write_text(roadmap,encoding='utf-8')
print('Prepared dev.15 documentation, package naming and requested roadmap additions')
