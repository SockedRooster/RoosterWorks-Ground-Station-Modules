# RoosterWorks Ground Modules — v0.8.0-dev.23 TEST

Adds an inline Ore refinery, a deployable mining rig and a universal hull
mounting shoe. 34 visible side pads with structural snap nodes are added to
straight ground hulls. Existing gameplay, geometry and plugins are preserved
apart from the additive equipment pads/nodes.

Requires KSP 1.12.5, ModuleManager and Station Modules v0.7.5-dev.5 or newer.
No new mod dependency. Ground LOG storage selection still requires Kerbalism
Default and Community Resource Pack. Ground Modules remains a separate addon.

Close KSP and replace only GameData/RoosterWorksGroundModules. Keep the core
Station Modules folder. Use newly placed parts for testing; existing craft
and saves are not migrated or edited.

ISRU stores 300 Ore (empty) and 1,000 EC. It offers LF+Ox, LF, Oxidizer and
Monopropellant modes. DRILL stores 50 Ore (empty) and 150 EC, consumes 7.5 EC/s,
and uses the stock deployable mechanism in an original RoosterWorks cradle.
Fit power, active radiators and separate fuel tanks. No industry part has
crew, habitat or shielding. No RCS or new docking ports are added to equipment.

Mounts are structural snap points. Existing end docking is preserved. The
VT pod retains its surface attachment and clean separation. HUB/ELB/FLEX and
the tapered endcap receive no fixed side pads; use a shoe on clear rigid skin.

See INDUSTRY.md for rates, mounting instructions, source paths, Kerbalism
behavior and testing limits. Native/configuration/preservation checks pass;
mining, heat management and attachment physics need confirmation in KSP.
This is a test candidate. No installed game files or saves were modified.

Current builder: Tools/build_v23.py. Validator: Tools/validate_v23.py.
Editable source: Source/Industry/RoosterWorks-Ground-dev23.blend.
Previews: Previews/dev23-*.png. Current archives are in ../outputs/.
Previous accepted LOG balance and utility behavior are retained from dev.22.
