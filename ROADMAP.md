# RoosterWorks roadmap

Station source baseline: v0.7.5-dev.5. Ground integration candidate: v0.8.0-dev.15. Earlier milestone descriptions below retain their development history; no publication/release status is implied.

## Planned milestones

| Version | Scope |
|---|---|
| 0.65 | Selectable ring colors on each module and selectable logistics contents — implemented in development candidate; KSP testing pending |
| 0.7 | 5 m station family and 3.75-to-5 m adapter — development candidate; KSP testing pending |
| 0.75 | Shorter HAB modules and longer crew tubes in 2.5 / 3.75 / 5 m; adjustable LAB storage and editor menu polish — development candidate; KSP testing pending |
| 0.8 | Land Base Station parts — Ground-base modules, including a vertical entry module with folding stairs |
| 0.9 | Adjustable legs or wheels for land bases |
| 0.95 | Large land base concepts |
| 1.0 | Attach modules to science/research tiers |

The requested “5mm station parts” is interpreted as 5 m, extending the current 2.5 m and 3.75 m families. The roadmap identifier 0.95 is retained as requested. Detailed specifications and implementation order within each milestone remain to be decided. The 1.0 milestone covers deliberate research/technology progression; current provisional TechRequired placements remain unchanged.

## 0.65 scope

- **Selectable ring colors on each module** — independent editor control: Original, Steel, White, Charcoal, Blue, Green, Red and Gold. Covers all 23 models, both diameters and connectors/adapters. Saved colors restore in flight.
- **Selectable logistics contents** — both LOG sizes offer Mixed supplies, Food, Water, Oxygen, Nitrogen, Ammonia, Waste and WasteWater in the editor. Mixed supplies remains the original default; waste tanks start empty; saved flight inventories remain untouched. LOG placement remains Station Utility.

0.65 is implemented as a development candidate, with live testing pending. 0.7 and 0.75 are implemented in this candidate; later scopes remain planned; no roadmap item establishes publication or release status. See CUSTOMIZATION_065.md for the complete acceptance checklist. The current family retains 41 native models/current catalogue parts with Kerbalism Default, plus two hidden historical reactor IDs for saved-vessel compatibility. Offline validation does not replace live KSP testing.

## Accepted ground-base visual direction

The living/science and access/services concept sheets are approved visual direction for 0.8/0.9, including the vertical entry module with folding stairs, rounded hubs, matching horizontal modules and adjustable supports. Concept images are plans, not completed game models.

## Added future work — 2026-10-15

- Top and bottom RCS thrusters for station/ground-module handling.
- Exterior module lighting.
- Dedicated thruster modules.

Milestone assignment, thrust, fuels, attachment layout and lighting controls
remain to be designed. These are roadmap items, not parts shipped in dev.15.
The separate SC-250 skycrane v0.1.0-dev.1 remains a local transport test build.


## Ground implementation candidate — dev.18 / 2026-10-15

The ground portion of the RCS, exterior-lighting and propulsion work is now
built for testing: top/bottom RCS on all twelve base modules, warm door
spotlights on HAB/CMD/EVA and a separate VT-60 vertical-lift pod. Orbital
station equivalents and exterior lights for other ground roles remain future
work. In-game validation is pending; this does not establish release status.


## Ground dev.19 correction

Integrated RCS is withdrawn at user request from all ground modules. Door
spotlight control and FLEX controls are revised for testing. VT-90 lift pod
replaces VT-60 statistics and gains clean whole-pod separation. Live KSP
confirmation remains pending; orbital station changes remain future work.

## Ground dev.20 test build

Sealed FLEX overlap boots and connected extension/retraction; science stair
light and solid lamp mounts; 25% longer three-seat command module with solid
dish and cleaned roof. Controller/native checks pass. Connected payload motion
still needs confirmation in KSP physics. Existing orbital roadmap stands.

## Ground dev.21

FLEX connection reinforcement and end-ring overlap correction. No roadmap scope change.

## Ground dev.22

Ground LOG dedicated capacities rebalanced; mixed supplies prioritize Food/Water/Oxygen. Added CO2/Hydrogen choices. Ground LOG/PWR have no habitat or shielding. No geometry/roadmap scope change.

## Ground dev.23 test candidate

Ground ISRU refinery, deployable Ore mining rig and universal equipment shoe.
34 visible rigid side mount pads/nodes on straight ground hulls. Stock fuel
recipes and drill animations; no new plugin dependency. Accepted modules,
LOG balance and VT separation retained. In-game mining/thermal/attachment
acceptance pending. Water/gas-specific mining and life-support chemistry are
future extensions rather than part of the first Ore/fuel implementation.


## Ground dev.24 test candidate

HPT-250 compact reinforced equipment collar: nominal 2.5 m, 1.2 m length, two integrated flat mounting saddles and side snap nodes, existing-size inline docking. Legless between supported modules. In-game attachment/physics acceptance pending.


## Ground dev.25 test candidate

Eight resource-specific Rooster drill variants use existing crustal deposits: MetalOre, MetallicOre, Minerals, Substrate, Uraninite, Lithium, RareMetals and Rock. Separate matching storage/processing remains required. No changes to planetary resources or current Ore ISRU recipes. In-game mining acceptance pending.

## Ground nuclear industry — dev.26 TEST

NST-250 storage, NSM-250 smelter and CEN-250 centrifuge are implemented as a development candidate. Uraninite drill → smelter → fictional feedstock → centrifuge → reactor fuel / depleted material. Matching legs, end docks, supported roof rails, service pipes, lights and independent colors. Existing installed CRP/SystemHeat providers required; power and active cooling required. No habitat or Shielding resource. See NUCLEAR_INDUSTRY.md. Native, configuration, color and packaging checks pass; live full-mod acceptance pending.

Ground dev.28 TEST: FLEX partial VAB Extension control (0–100%, 0.1% steps), live length readout and saved intermediate lengths; existing 1.2–4 m travel and connected-branch motion retained. See ADJUSTABLE_CREW_TUBE.md. Offline checks pass; live VAB confirmation pending.

Ground dev.29 TEST: restored CMD outer roof skin and seated communications/roof-panel fittings. Existing runtime, models and gameplay retained. See COMMAND_ROOF_FIX.md.

Ground dev.30 TEST: matching three-unit PWR side equipment on both sides; removed overlapping decorative service console. See POWER_SIDE_EQUIPMENT.md.
