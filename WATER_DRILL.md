# RoosterWorks Water Drill — dev.31

DRILL-H2O is a separate crewless rig in Harvesting alongside the other drills.
It mines underground Water using existing Community Resource Pack crustal maps.
Scan for Water and choose a site with nonzero abundance; water availability
depends on the installed planet maps. Ocean and atmospheric water are separate.

The rig has the existing half-scale deployable drill, 2.71 m contact reach,
engineer bonuses and core heat. Provide 7.5 EC/s, radiator cooling and ground
contact. Onboard storage: 150 EC and 250 units / 250 L of Water, initially empty.
Connect external Water storage for sustained extraction. Dry mass: 0.65 t;
empty price: 4,800 funds. Output varies with abundance, engineer and temperature.

Requires Station Modules and Community Resource Pack, as with the other CRP
mineral drills. No resource distribution or conversion recipe is added.
No extra plugin is needed. Existing parts and runtime binaries are preserved.

Close KSP, replace GameData/RoosterWorksGroundModules with this complete package,
then restart. Do not install a second copy alongside the previous version.
Offline configuration, preservation and archive checks pass; live KSP testing
remains pending. Preview: Previews/dev31-Drill-H2O.png. Editable owned frame:
Source/WaterDrill/RW_WaterDrillFrame.blend. Stock drill assets are referenced
from KSP and are not redistributed or embedded in the saved source scene.
