# RoosterWorks ground nuclear industry — dev.26 TEST

Three matching 2.5 m, 2.4 m-long utility modules. Each has four retractable
legs, supported yellow roof handrails, continuous underside service pipes,
two size-2 docking ports, end lights and independent finish/ring colors.
All prior parts, meshes, recipes and plugins are preserved.

| Part | Function | Empty cargo capacities | Dry mass |
|---|---|---|---|
| NST-250 Nuclear Materials Vault | Dedicated raw, intermediate, fuel and waste storage | Uraninite 1000; RW Nuclear Feedstock 500; EnrichedUranium 200; DepletedFuel 200 | 4.8 t |
| NSM-250 Nuclear Smelter | Uraninite → RW Nuclear Feedstock | Uraninite 250; feedstock 250 | 5.5 t |
| CEN-250 Fuel Centrifuge | Feedstock → reactor fuel and depleted material | Feedstock 250; EnrichedUranium 40; DepletedFuel 200 | 6.0 t |

All nuclear cargo starts empty; EC buffers start full (500 / 1000 / 1500).
No crew, habitat, Shielding resource, reactor or power generation is added.
The vault's exterior casks and dry mass represent its protective structure;
they do not add a Kerbalism habitat/shielding bonus.

## Operation

1. Mine **Uraninite** with the existing URN specialist drill at a surveyed
   deposit. These parts do not add deposits or alter existing resource maps.
2. Connect the smelter, centrifuge and vault, with power and active SystemHeat
   radiators. Raise/retract legs and dock as with the existing ground family.
3. Start Nuclear Smelting: **0.02 Uraninite/s + 60 EC/s → 0.01 feedstock/s**,
   producing **54 kW** of process heat.
4. Start Fuel Separation: **0.01 feedstock/s + 120 EC/s → 0.0001 EnrichedUranium/s
   + 0.0067 DepletedFuel/s**, producing **108 kW** of heat.
5. Empty the centrifuge's fuel and depleted tanks into compatible containers
   using its SystemHeat fuel-transfer controls. A level-3 Engineer is required.
   These outputs remain local **NO_FLOW** resources, respecting CRP/NFE rules;
   permanent docking crossfeed does not make nuclear fuel transfer automatically.

These are abstract KSP balance recipes, not real nuclear processing models.
RW Nuclear Feedstock is a new fictional, pumpable intermediate, not a mined
resource. Each converter shuts down at 850 K and will stop if its required
input is absent or either output is full; no fuel or waste is silently dumped.
The nominal rates above have no Engineer multiplier. SystemHeat's efficiency
curve applies; rates depend on the thermal loop state. Fit at least 162 kW
of radiator capacity at the operating temperature for both processors together,
plus separate drill/craft cooling needs. External power generation is required.
The centrifuge is an enclosed stationary exterior model; no visible spin is added.

## Requirements and installation

KSP 1.12.5, ModuleManager, RoosterWorks Station Modules dev.5 or newer,
Community Resource Pack and **SystemHeat**. Those providers are present in
the inspected installation. The three new parts hide if a required provider
is absent. SystemHeat's installed assembly supplies the converter and nuclear
fuel-transfer modules; no new DLL or global resource-flow patch is supplied.
The existing Kerbalism/SystemHeat converter bridge can handle these converters
when installed/enabled. Background/full-mod behavior still needs a live test.

Close KSP and replace only `GameData/RoosterWorksGroundModules` from the ZIP.
Keep Station Modules and the installed resource/thermal providers. This is a
complete ground package, not a second folder to install alongside an older copy.
Parts are in Utility / Station Utility with VABOrganizer; search NST, NSM or CEN. Ground drills are in Utility / Harvesting.

## Verification and acceptance

Native/configuration checks cover transforms, docking, leg bindings, finite
geometry, physical colliders, textures, original ring maps, converter recipes,
resource dependencies, output mass, empty tanks and preservation of dev.25.
Editable Blender scenes and the previews use the actual new native models.
Archive payloads, CRCs and checksums are checked after packaging.

Live KSP acceptance remains pending: spawn the three parts; cycle legs and
finish/ring colors; dock the line; run converters with/without inputs, cooling
and output capacity; test level-3 Engineer fuel transfer to the vault and the
target reactor; then reload the vessel and test background processing with
the complete installed mod set. No installed game files or saves were changed.

Dev.27 mounting correction: closed curved saddles join the hull to each equipment rack, with steel cheek brackets and captive bolts. Original geometry, configs, capacities, recipes, controls and plugins are preserved; only three native models and the version change. Checked through 21 leg poses; live KSP confirmation pending.

Dev.27 final: matching equipment and hull saddles are fitted on BOTH flanks. Occupied exterior pad nodes are removed. Storage capacities, processing rates and dry masses remain unchanged. Empty/default VAB prices: NST 24,000; NSM 36,000; CEN 68,000. Configured full-tank prices include the resource allowance so empty tanks no longer drive the displayed cost negative; adding cargo increases the price normally.

