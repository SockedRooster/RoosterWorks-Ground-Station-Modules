from pathlib import Path
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'work/python-deps'))
import dnfile
p=dnfile.dnPE('D:/SteamLibrary/steamapps/common/Kerbal Space Program/KSP_x64_Data/Managed/Assembly-CSharp.dll')
for t in p.net.mdtables.TypeDef:
 if str(t.TypeName) in ('ModuleLight','ModuleColorChanger'):
  print(t.TypeName,[(str(f.row.Name),'public' if f.row.Flags.fdPublic else 'private') for f in t.FieldList])
