"""Workspace index only, then keep the two latest verified ground distributions."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
validation=json.loads((R/'Reports/PACKAGE_VALIDATION.json').read_text())
for name,info in validation.items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==info['sha256']
for line in (OUT/'RoosterWorks-Ground-Modules-v0.8.0-dev.25-SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
path=W/'WORKSPACE_INDEX.md';text=path.read_text(encoding='utf-8-sig');start=text.index('Latest ground build:');end=text.index('Updated October',start)
note='''Latest ground build: **ground-hotpatch-v26 / v0.8.0-dev.26 TEST**, superseding
dev.25. Adds NST-250 Nuclear Materials Vault, NSM-250 Nuclear Smelter and
CEN-250 Fuel Centrifuge, with matching 2.5 m hulls, retractable legs, end
docking, supported rails, service pipes, lights and finish/ring controls.
Uraninite → fictional RW Nuclear Feedstock → EnrichedUranium / DepletedFuel.
Requires installed CRP/SystemHeat; external power and active cooling. No
habitat or Shielding. Empty nuclear cargo; Engineer-controlled fuel transfer.
28 parts / 20 native models; all dev.25 GameData preserved except version.
4,390 native/configuration checks and 11,184 actual-source color assertions
pass, plus archive CRC/byte/manifest checks. Live full-mod acceptance pending.
Editable models: Source/Nuclear/RoosterWorks-Ground-dev26.blend. Details in
NUCLEAR_INDUSTRY.md; family preview in Previews/dev26-NuclearFamily.png.
Complete installation/source ZIPs are in outputs/.

'''
text=text[:start]+note+text[end:]
text=text.replace('| Ground Modules | 0.8.0-dev.25 | 0.8.0-dev.24 | ground-hotpatch-v25 / ground-hotpatch-v24 |','| Ground Modules | 0.8.0-dev.26 | 0.8.0-dev.25 | ground-hotpatch-v26 / ground-hotpatch-v25 |')
text=text.replace('Current builders, regression checks and source-preservation manifests still require','Current builders, regression checks and source-preservation manifests still require ground-hotpatch-v24 and ground-hotpatch-v25, plus')
path.write_text(text,encoding='utf-8')
context=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';previous=context.read_text(encoding='utf-8-sig')
heading='# Current ground build — October 16, 2026: dev.26 nuclear industry\n\n'
if not previous.startswith(heading):context.write_text(heading+note+'Previous notes follow.\n\n'+previous,encoding='utf-8')
# User requested only the two newest distributable versions. Historical source
# folders are still protected builder/validation dependencies, so retain those.
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 old=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.24-'+suffix)).resolve()
 assert old.parent==OUT.resolve() and old.is_relative_to(W.resolve())
 if old.exists():
  removed.append({'path':old.relative_to(W).as_posix(),'bytes':old.stat().st_size,'sha256':hashlib.sha256(old.read_bytes()).hexdigest()});old.unlink()
(R/'Reports/DEV26_RETENTION.json').write_text(json.dumps({'retained_distributions':['0.8.0-dev.26','0.8.0-dev.25'],'historical_source_dependencies_retained':True,'removed':removed},indent=2)+'\n')
print('PASS verified both retained ground distributions, updated workspace index/context and retained only dev.26/dev.25 distribution archives')
