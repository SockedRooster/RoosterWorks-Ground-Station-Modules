# HPT-250 compact equipment collar — v0.8.0-dev.24 TEST

An original short ground-base section inspired by the reference's solid side
mounts, using the established RoosterWorks ground appearance. It is 1.2 m long,
has nominal 2.5 m inline interfaces and two opposed flat hardpoints. Place it
between supported modules as a dedicated equipment bay.

## Shape and attachment

The center shell is flattened and shaped into two reinforced saddles rather
than placing unsupported boxes on a round cylinder. Black bases intersect the
shell, stepped steel shoulders carry the load, and flat White/Grey receiving
plates have captive fasteners and alignment marks. Their outer faces are at
Z=+1.25 m and Z=-1.25 m: the complete side mounts remain within 2.5 m across.
Each usable central flat face is 0.70 m wide along the module axis and 0.88 m
high. The broader stepped saddle is approximately 0.92 m by 1.18 m.

Both sides accept surface attachment against real flat receiving colliders,
and each has a central size1 structural snap node. They are equipment mounts,
not additional docking ports. The DRILL rear node can snap directly to one.
The existing VT pod remains surface-attached so its established whole-pod
separation works as before. The mounted preview illustrates a balanced pair
of existing VT pods; they are separate parts and are not included in HPT mass.

The two inline ends retain size2 docking, the strong ground acquisition
settings, permanent resource crossfeed and no docking staging. Both mating
planes stay clear. The short section has no legs: adjacent supported modules
carry it, just as they carry a legless connection section. It cannot level or
support a standalone base by itself. Keep external loads balanced and clear
of neighboring stairs, legs and equipment. New surfaces do not turn surface
attachments into docking connections or add automatic mechanical alignment.

## Appearance and role

White/Grey metal shell finishes, independent interface ring colors, ivory
cladding, bronze trim, recessed endcaps, upright end badges and illuminated
end windows match the set. Yellow/copper roof rails have black hull sockets.
The roof label has a solid backing. Paired underside service pipes extend to
both ends at the existing ground-family endpoints, so neighboring parts join
without a gap. Ring colors do not recolor the side receiving plates.

It weighs 1.0 t, costs 2,400 funds and has 2,000 breaking-force/torque limits.
It has no crew, IVA, exterior EVA hatch, habitat, shielding, tanks, propulsion,
RCS or deployable hardware. Optional Connected Living Space marks the inline
passage passable. It appears under Structural / Station Connectors with VAB
Organizer (crewTubes), or search HPT-250 / equipment collar.

## Install and checks

Requires KSP 1.12.5, ModuleManager and Station Modules dev.5 or newer. No new
plugin is needed. Close KSP and replace only GameData/RoosterWorksGroundModules;
keep the separate station addon. Restart and place a new HPT-250 between two
supported modules. Test both inline interfaces, both side surfaces/nodes,
module lights, appearance selectors and loaded equipment. Existing craft
and flight saves are not migrated or edited.

All sixteen existing ground models/part configs, shared textures, compatibility
patches and plugin binaries are byte-for-byte unchanged. Only the version and
the new collar's model, part, label and compatibility file are added. The
dev.23 refinery, drill, universal shoe and 34 prior small hull pads remain.
Station Modules is also unchanged.

1,818 native/configuration/preservation checks cover the 1.2 m axial envelope,
2.5 m side width, planar receiving faces, collider/node agreement, editor ray
hits, outward mirrored bevel normals, independent shell backing, fixed docking
transforms, native winding/UVs, convex collision limits, emission controls,
scoped maps and baseline hashes. 3,728 actual-source ring-color assertions
exercise the new real map through colors, menu reopen/reset and ownership
cleanup. Full KSP physics and mod-load acceptance remain pending; this is a
test candidate. No installed game files or saves were changed.

Builder: Tools/build_v24.py. Validator: Tools/validate_v24.py.
Editable source: Source/Hardpoint/RW_GND_HPT.blend, including a separate
mounting-demonstration scene. Previews: Previews/dev24-*.png.
Renderer: Tools/create_hardpoint_blend.py. All reference geometry and prior
builds are read-only. The adjacent ground-hotpatch-v23 and rw-v075dev5 source
helpers are needed to rebuild, not to install the packaged addon.
