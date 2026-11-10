from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];W=R.parent
out={}
for folder in ('rw-v075dev5','ground-modules-art-v4','ground-hotpatch-v19','skycrane-v010dev1'):
 for p in (W/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:out[p.relative_to(W).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'Reports').mkdir(exist_ok=True)
(R/'Reports/READ_ONLY_INPUTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('Captured',len(out),'existing file hashes; originals protected')
