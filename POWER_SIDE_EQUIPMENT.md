# PWR side equipment — dev.30 TEST

The ground PWR module now has the same three external service accumulators on
both sides, including all six retaining straps and three valves per bank.
The opposite bank is an exact native copy rotated 180 degrees about the module's
vertical axis, preserving its appearance and outward normals.

Removed the service console that overlapped the middle accumulator: enclosure,
face, screen, three status LEDs and console lettering. No controls were removed
from the part's menus; the removed console was exterior decorative geometry.

Battery/reactor variants, power generation/storage, fuel, mass, cost, docking,
end lights, supported roof rails, underside pipes, hull mounting pads and
leg animation are unchanged. The new bank clears the end mounting pads and
lower RoosterWorks label. All other parts and plugin binaries are preserved,
including the CMD roof repair and the adjustable FLEX tube.

1,825 native/selection/preservation checks and 3,728 actual-source color
assertions pass. Checks verify exact geometry selection, complete console
removal, identical opposite bank, finite geometry and unchanged ring maps.
Editable before/after scenes: Source/PowerSides/RW_GND_PWR-dev30.blend.
Previews/dev30-Power-After.png and -Opposite.png show the actual native model.
Both archives undergo source-byte, CRC and manifest checks. Live KSP visual
confirmation remains pending.

Close KSP, replace only GameData/RoosterWorksGroundModules from the complete
dev.30 package and restart. Keep Station Modules as the separate addon.
