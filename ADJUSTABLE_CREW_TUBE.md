# Adjustable FLEX crew tube — dev.28 TEST

In the VAB, right-click **RoosterWorks Ground FLEX — Collapsible Crew Tube**.
Use **Extension** to choose an intermediate deployment amount. The slider runs
from 0% (1.2 m overall length) to 100% (4.0 m), in 0.1% steps: approximately
2.8 mm of length per step. **Tube length** shows the current overall length
in meters to three decimal places while the tube moves.

Attach the fixed/rear end, then adjust Extension until the moving end fills
the gap. Modules and children connected to that moving end follow the change.
The moving-end-parent tree orientation is supported too. Let the motion
settle before taking the final measurement or attaching the far end.
Both existing Extend/Collapse buttons remain available. Custom intermediate
lengths use the existing persisted extension/target fields, so saving,
reloading and reopening the part menu preserve them without changing old saves.

The slider is editor-only. In-flight Extend/Collapse, driven joint motion,
tether release, strong fittings, warp/packed-vessel pauses and docking-capture
guards retain their behavior. A closed rigid connection loop must still be
opened before resizing: stretching a tube cannot reshape a locked loop.
This adds fine adjustment within the existing travel, not extra maximum length.

All 20 native models and other part configs are unchanged. The shared ground
DLL is rebuilt with the single FLEX controller change; all other runtime
source files are unchanged. Nuclear module prices, matching side equipment
and the requested Harvesting/Station Utility catalogue placement are retained.

The controller compiles against the installed KSP 1.12.5 assemblies. 1,254
actual-source behavioral assertions cover partial selections, readout, holding,
reopen/reload, branch motion in both tree orientations and closed loops, plus
the existing flight/editor motion cases. Configuration/preservation and archive
checks pass. Live VAB/complete mod-set confirmation remains pending.

Close KSP, replace only `GameData/RoosterWorksGroundModules` from the complete
dev.28 ZIP, keep Station Modules and restart. Existing resource/thermal
dependencies for the nuclear parts remain as described in NUCLEAR_INDUSTRY.md.
