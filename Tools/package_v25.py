from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];OUT=R.parent/'outputs';OUT.mkdir(exist_ok=True)
assert 'PASS dev.25: 1992' in (R/'Reports/v25-validation.log').read_text()

log=(R/'Reports/v25-render.log').read_text()
for label in ('MetalOre','MetallicOre','Minerals','Substrate','Uraninite','Lithium','RareMetals','Rock'):
 assert 'PASS rendered specialist '+label in log
 assert len(list((R/'Previews').glob('dev25-Drill-*.png')))==8
assert 'PASS packed eight editable specialist frames; stock assets not embedded' in log
assert (R/'Source/MiningVariants/RW_MineralDrillFrames.blend').stat().st_size>1000000
files=sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.blend1') and p.name not in ('package.log','PACKAGE_VALIDATION.json') and (p.relative_to(R).parts[0]!='Previews' or p.name.startswith(('dev23-','dev24-','dev25-'))))
install=[p for p in files if p.relative_to(R).parts[0] in ('GameData','Previews') or p.name in ('README.md','ROADMAP.md','INDUSTRY.md','COMPACT_HARDPOINT.md','MINERAL_DRILLS.md','CHECKSUMS-SHA256.txt')]
results={};payloads=[]
for suffix,entries in (('HOT-PATCH',install),('HotPatch-Source',files)):
 out=OUT/f'RoosterWorks-Ground-Modules-v0.8.0-dev.25-{suffix}.zip'
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in entries:
   i=zipfile.ZipInfo(p.relative_to(R).as_posix(),(2026,10,16,12,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16;z.writestr(i,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for name in z.namelist():
   assert z.read(name)==(R/name).read_bytes()
   if name.startswith('GameData/'):assert name.startswith('GameData/RoosterWorksGroundModules/')
   assert 'TriBitDrill.mu' not in name and 'TriBitDrill.dds' not in name
  assert len([n for n in z.namelist() if n.startswith('GameData/') and n.endswith('.mu')])==17
  assert len([n for n in z.namelist() if n.startswith('GameData/') and '/Parts/' in n and n.endswith('.cfg')])==25
  for line in z.read('CHECKSUMS-SHA256.txt').decode().splitlines():
   digest,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==digest
  payloads.append({n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('GameData/')})
 results[out.name]={'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'files':len(entries)}
 print('PASS industry archive CRC, source bytes, scoped GameData, 25 parts / 17 reused models and manifest:',out.name,flush=True)
assert payloads[0]==payloads[1]
(OUT/'RoosterWorks-Ground-Modules-v0.8.0-dev.25-SHA256SUMS.txt').write_text(''.join(v['sha256']+'  '+k+'\n' for k,v in results.items()))
(R/'Reports/PACKAGE_VALIDATION.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
