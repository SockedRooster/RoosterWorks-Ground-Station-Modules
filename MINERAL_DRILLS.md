# Specialist mineral drills — v0.8.0-dev.25 TEST

Eight new RoosterWorks drill parts mine solid resources already defined and
mapped in the user's installed setup. They share the existing native cradle
and half-scale stock deployment mechanism. Each has a resource-specific title,
label and colored upper housing. Choose the specialist in the VAB before
launch; these are separate parts, not in-flight switchable harvesters.

| Code | Extracted resource | Buffer units | Nominal buffer volume | Required resource provider |
|---|---|---:|---:|---|
| MET | MetalOre — Metal Ore | 50 | 250 L | Extraplanetary Launchpads or SimpleConstruction |
| MTO | MetallicOre — Metallic Ore | 250 | 250 L | Community Resource Pack |
| MIN | Minerals | 250 | 250 L | Community Resource Pack |
| SUB | Substrate | 250 | 250 L | Community Resource Pack |
| URN | Uraninite | 250 | 250 L | Community Resource Pack |
| LTH | Lithium | 250 | 250 L | Community Resource Pack |
| RAR | RareMetals — Rare Metals | 250 | 250 L | Community Resource Pack |
| RCK | Rock | 250 | 250 L | Community Resource Pack |

MetalOre and MetallicOre are different resource IDs and require matching
containers and processors. The MET and MTO rigs are intentionally distinct.
Uraninite is raw feedstock; the rig does not directly produce EnrichedUranium.

Each part is 0.65 t dry and costs 4,800 funds. It starts with 150 EC and an
empty mineral buffer, draws 7.5 EC/s when operating, and retains the established
2.71 m contact reach, deploy/run animations, engineer bonuses, thermal curves,
overheat shutdown and radiator requirement. The 250 L collection volume matches
the original 50-unit Ore buffer using installed resource unit volumes. Resource
mass differs with density. Rated efficiency is normalized by unit volume:
0.75 for five-litre MetalOre units, 3.75 for one-litre resources. Actual output
still depends on local abundance, temperature and engineer skill. A zero
harvest threshold permits trace deposits; zero abundance still yields no mineral.

## Using the rigs

Find the specialist in Utility / Resources with VAB Organizer, or search its
resource name or DRILL code. Mount it upright on a clear hull face or snap its
rear node onto an HPT-250 side node or a suitable existing equipment pad.
The original drill's mounting dimensions are unchanged. Lower the base's
support legs, supply sustained electricity and active radiators, deploy the
drill and start the named resource extractor.

Use an existing scanner/resource overlay and choose a site with a nonzero
crustal deposit. These are surface mining rigs: they do not harvest oceans,
atmospheres, asteroids or resources from empty space. Planet, biome and save
seed affect availability. Some materials occur only on a few mapped worlds;
for example, the installed positive RareMetals records target Bub. The code
does not add, redistribute or guarantee mineral deposits.

The installed ModuleManager cache was read to verify each resource definition
and at least one positive crustal distribution before building. A filtered,
read-only snapshot and cache hash are recorded in
Source/MiningVariants/InstalledResourceInventory.json. No game cache, resource
map, planet configuration or save is modified. Missing optional providers hide
the relevant specialist parts. Community Resource Pack defines resources;
the installed planet/resource mods supply the actual deposits.

Fit matching bulk tanks and processing equipment for extended operations.
The original RoosterWorks Ore drill, life-support LOG loadouts and Ore-only
ISRU recipes are unchanged. This update does not add mineral conversion
recipes, water/gas extraction, automatic processing or automatic cargo refills.

## Installation and verification

Requires KSP 1.12.5, ModuleManager, Station Modules dev.5 or newer and the
applicable resource provider. Close KSP, replace only
GameData/RoosterWorksGroundModules and restart. Keep the separate Station
Modules folder. Test freshly placed specialist parts; existing craft and saves
are not migrated or edited. New resource-provider dependencies apply only to
the new specialists; the original Ore rig remains available as before.

All seventeen existing ground native models, existing part configurations,
textures, compatibility patches and plugin binaries are byte-for-byte unchanged.
No new DLL or MU model is required: native MODEL texture remaps identify each
specialist. The stock drill model and animations remain local KSP references;
no Squad meshes or textures are redistributed.

1,992 configuration/resource/preservation checks cover exact resource IDs,
positive installed map records, dependency gates, volume-normalized buffers
and efficiency, empty starting cargo, resource-specific actions, native remaps,
unchanged stock mechanism/heat/mount settings, scoped additions, protected
baselines and manifests. In-game mining, physics, thermal balance and full
mod-load acceptance remain pending; this is a test candidate.

Builder: Tools/build_v25.py. Validator: Tools/validate_v25.py.
Editable colored frames: Source/MiningVariants/RW_MineralDrillFrames.blend.
The saved Blender file contains only owned frames and references; the renderer
loads the installed stock mechanism only after saving to show assembled rigs.
Renderer: Tools/create_mineral_drill_blend.py. Current previews use dev25 names.
The adjacent ground-hotpatch-v24 and rw-v075dev5 source helpers are needed to
rebuild; the filtered resource snapshot makes the build reproducible without
depending on a changing live resource cache. Installation uses the ZIP alone.
