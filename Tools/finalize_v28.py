from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;OUT=W/'outputs'
for version in (27,28):
 for line in (OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.{version}-SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
note='''Latest ground build: **ground-hotpatch-v28 / v0.8.0-dev.28 TEST**, superseding
dev.27. FLEX gets a persistent editor-only Extension slider, 0–100% in 0.1%
steps (2.8 mm), plus a live 3-decimal meter length readout. Existing 1.2–4 m
range, buttons, connection strength and flight actuator retained. Partial VAB
movement pushes/draws the connected branch in either tree orientation;
closed loops remain guarded. Saved partial amounts persist. Actual KSP 1.12.5
API compilation, 1,254 controller assertions, 1,660 preservation/configuration
checks and both archive CRC/manifest/byte checks pass. All 20 native models,
other parts, nuclear prices and Harvesting/Station Utility placement retained.
Only the shared ground DLL, FLEX description and version change in GameData.
Live VAB confirmation pending. Complete install/source ZIPs in outputs/;
ADJUSTABLE_CREW_TUBE.md has usage. Previous dev.27 distributions retained;
historical source baselines remain build dependencies.

'''
p=W/'WORKSPACE_INDEX.md';t=p.read_text(encoding='utf-8-sig');start=t.index('Latest ground build:');end=t.index('Updated October',start);t=t[:start]+note+t[end:]
t=t.replace('| Ground Modules | 0.8.0-dev.27 | 0.8.0-dev.26 | ground-hotpatch-v27 / ground-hotpatch-v26 |','| Ground Modules | 0.8.0-dev.28 | 0.8.0-dev.27 | ground-hotpatch-v28 / ground-hotpatch-v27 |');p.write_text(t,encoding='utf-8')
p=W/'ROOSTERWORKS_DEVELOPMENT_CONTEXT.md';t=p.read_text(encoding='utf-8-sig');heading='# Current ground build — October 17, 2026: dev.28 partial VAB crew-tube deployment\n\n'
if not t.startswith(heading):p.write_text(heading+note+t,encoding='utf-8')
removed=[]
for suffix in ('HOT-PATCH.zip','HotPatch-Source.zip','SHA256SUMS.txt'):
 p=(OUT/('RoosterWorks-Ground-Modules-v0.8.0-dev.26-'+suffix)).resolve()
 assert p.parent==OUT.resolve() and p.is_relative_to(W.resolve())
 if p.exists():removed.append({'path':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});p.unlink()
(OUT/'Ground-dev28-retention.json').write_text(json.dumps({'kept':[28,27],'historical_source_baselines_retained':True,'removed':removed},indent=2)+'\n')
print('PASS current/previous archive hashes, workspace index and two-version distribution retention')
