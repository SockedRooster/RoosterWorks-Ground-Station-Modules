# Ground Modules dev.32 — leveling, drill heat and FLEX warp repair

## Level the connected station

On the ground command module select **Auto-Level Station** after landing.
It lowers all connected RoosterWorks supports and stairs, fits each support
to the static ground surface and gently levels the connected assembly through
physics. Hulls and docked modules are never individually teleported or rotated.
Use **Stop Auto-Leveling** to hold the current support lengths without further
adjustments. Support lengths and stair angles are saved with the craft/vessel.

Foot travel is 0.65 m farther down or 0.35 m above the ordinary deployed pose.
The foot pads keep their dimensions; the telescopic transition changes length
while the upper connection remains fixed. Stair runs adjust by up to 15 degrees;
the top landing and boarding/grab trigger stay against the door. Foot colliders
and stair colliders follow the visible hardware.

The controller accepts moderate slopes up to 8 degrees, subject to every foot
and stair run reaching the surface. A wide station may run out of support
travel on a gentler slope; the status reports this instead of forcing it level.
It ignores vessels/parts and trigger volumes when probing terrain, accepts
static landing surfaces, and waits if terrain is missing. Lowering stairs before
EVA is still required. This feature adjusts supports on the connected vessel;
separate undocked vessels need their own command module.

An existing ground tether releases for leveling and re-enables after all
supports settle and the command module is within 0.2 degrees of level. An
enabled tether freezes leveling. It pauses during loading, warp, flex-tube
movement, throttle/wheel input, significant motion or if no longer landed.
Do not expect supports to compensate for cliffs or gaps beyond their travel.

## Drill heat loops

All ten drills (Ore, eight mineral specialists and Water) now use SystemHeat
when installed. Use its normal **heat loop selector** in the part menu to choose
the radiator circuit. Every rig draws 7.5 EC/s and produces 7.5 kW of process
heat at nominal load, with 0.25 m³ coolant volume and a 350 K outlet target.
Efficiency remains full through 400 K and declines to zero at 650 K, the
overheat shutdown threshold. Radiators must support the loop's temperature.

The old stock core-heat and temperature curves are removed in this path to
avoid two heating systems. Resource unit size no longer multiplies heat:
Water and dense ore rigs use the same heat budget for the same electric draw.
Extraction abundance, buffer sizes, engineer bonuses, contact reach and drill
animations remain unchanged. Without SystemHeat, the original stock thermal
behavior remains as a fallback. With the installed Kerbalism SystemHeat bridge,
the harvester uses its background-compatible class and matching reliability type.

## FLEX time warp

FLEX now commits the current physical station shape to KSP's packed part
positions before time warp and saving. Its visible bellows keep the saved
partial/full extension while packed. On unpack, the rebuilt moving-end joint
starts with matching anchors, avoiding the old collapsed rest shape and spring
preload. The normal joint-driven pushing/resizing mechanism is preserved.

Existing saves retain their saved extension. If a save was already made with
the wrong collapsed station positions, this patch preserves those actual saved
positions; it cannot infer the lost layout. Rebuild or reposition that affected
connection once before saving again.

## Installation and validation

Close KSP, replace **GameData/RoosterWorksGroundModules** with this complete
dev.32 package, then restart. Keep the Station Modules dependency installed.
No new models/textures or station-addon changes are required.

Compiled against the installed KSP 1.12.5 assemblies. Automated checks cover
the real support deformation/controller code, mesh/collider agreement, landing
and trigger preservation, terrain/travel guards, connected bodies and tether
recovery; FLEX tests repeat pack/unpack at partial/full lengths and verify zero
anchor preload. The thermal patch is checked against the installed SystemHeat
and Kerbalism bridge types. Package contents and previous assets are verified.
Live KSP physics and final ModuleManager patch-cache acceptance remain pending.
