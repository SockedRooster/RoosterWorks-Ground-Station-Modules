# Ground industry — v0.8.0-dev.23 TEST

This is a complete replacement of the Ground Modules addon folder. It keeps
the existing ground parts and adds three parts. Station Modules remains a
separate required addon; v0.7.5-dev.5 or newer is compatible, including dev.9.
KSP 1.12.5 and ModuleManager are required. No new dependency is introduced.

## Parts

| Part | Role | Dry mass | Storage |
|---|---|---:|---|
| Ground ISRU | 2.5 m inline Ore refinery; two docking ends, four retractable legs | 5.25 t | 300 Ore empty; 1,000 EC full |
| Ground DRILL | Deployable, hull-mounted mining rig | 0.65 t | 50 Ore empty; 150 EC full |
| Ground MOUNT | Universal surface-mounted equipment shoe with outward snap node | 0.025 t | None |

The ISRU retains the accepted ground barrel, roof handrails, supported legs,
seamless utility pipes, end-window lights and strong manual docking controls.
Three new exposed process vessels, plumbing and a dedicated refinery label
distinguish it from PWR. It has no reactor, crew, habitat or shielding.

The DRILL combines an original RoosterWorks cradle with the installed stock
Drill-O-Matic mechanism at half scale, sized to the ground-family centerline.
Its stock deploy/run animations remain native. Neither Squad's model nor its
textures are redistributed. The editable Blender file includes our cradle;
the preview tool loads the stock mechanism from the local KSP installation
only after saving the source file. Preview images show the assembled part.

## Mining and conversion

Start with a connected powered base on Ore-bearing land, with support legs
lowered. Attach the drill upright to a side pad or a clear rigid hull panel,
with its head pointing down. Select Deploy Drill, then Start Ore Drill.
The drill draws 7.5 EC/s and has half the large stock drill's base efficiency;
Ore abundance, temperature and engineer skill affect the actual rate. Its
2.71 m terrain-contact range reaches the ground below the standard hull.
It is a surface Ore drill; asteroid, comet and water/gas mining are not added.

The refinery has four stock recipe modes, each drawing 30 EC/s while active:

| Mode | Ore/s | Output/s at nominal efficiency |
|---|---:|---|
| LF + Oxidizer | 0.50 | 0.45 LiquidFuel + 0.55 Oxidizer |
| Monopropellant | 0.50 | 1.00 MonoPropellant |
| LiquidFuel | 0.45 | 0.90 LiquidFuel |
| Oxidizer | 0.55 | 1.10 Oxidizer |

Stock thermal curves, overheat shutdown and engineer bonuses are retained.
Fit **active radiators, a sustained power source and destination fuel tanks**.
The process vessels are visual equipment; they are not free cooling or fuel
storage. Ore buffers start empty. The fixed recipes consume Ore and power;
they do not create free propellant or refill other modules automatically.

With Kerbalism installed, these new IDs retain stock Ore harvesting/conversion
modules. They do not inherit the Default profile's stock-part-only chemical
plant replacement. Food/water/gas chemistry is future scope. Generic Kerbalism
planner/reliability support can still apply. Full in-game/background behavior
with the user's complete mod set remains to be confirmed.

## Hull equipment attachment

34 rigid side pads now have named size-1 structural snap nodes. HAB, LAB,
CMD, LOG, GRN, AIR, PWR and straight TUB each have four: port/starboard near
both end collars. ISRU has two on the clear flank; its process skid occupies
the other side. Pads have black bases, steel faces, captive bronze bolts and
colliders flush with the exposed node. Original docking planes are unchanged.

These nodes provide structural attachment and resource crossfeed; they are
not additional docking ports. In the VAB, use node snap to fit DRILL or MOUNT.
Rotate the rig as needed so the mast stays upright on either flank. Leave the
drill stroke clear of stairs, supports and other equipment. Adjacent modules'
nearby collar pads are alternative mounting positions, not space for two
overlapping large rigs. Choose an unobstructed bay for each installation.

All existing hulls already allow surface-mounted children. The separate MOUNT
shoe provides an outward node on another clear rigid panel. Curved HUB/ELB,
tapered endcaps and moving FLEX sections receive no fixed pads in this build.
Use shoes on clear rigid skin only; do not attach equipment to bellows or
other moving geometry. The existing VT pod remains surface-attached so its
established whole-pod release behavior is preserved.

## Install and verification

Close KSP, replace only `GameData/RoosterWorksGroundModules`, and restart.
Keep `GameData/RoosterWorksStationModules`. Place fresh parts to test the new
snap nodes; loaded craft are not migrated. This build does not edit installed
game files, craft files or saves.

Native checks cover existing geometry preservation, five actual stock drill
poses, downward terrain-contact rays, resources and recipe mass balance,
mount/node agreement, ring-map grammar, materials, normals, winding,
colliders, baseline hashes and the manifest. All existing plugin binaries
are unchanged. In-game mining, thermals, physics and the full mod load still
need confirmation; this is a test candidate.

Current builder: `Tools/build_v23.py`; validator: `Tools/validate_v23.py`.
Packaged editable source: `Source/Industry/RoosterWorks-Ground-dev23.blend`.
Run `Tools/create_industry_blend.py` with Blender to rebuild the source and
previews. The tools use adjacent `rw-v075dev5` developer helpers and the
protected `ground-hotpatch-v22` baseline. Stock settings are recorded in
`Source/Industry/StockModuleTemplates.cfg` for reproducibility.
