from pathlib import Path
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'work/python-deps'))
import dnfile
base=Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/KSP_x64_Data/Managed')
for dll,names in [('Assembly-CSharp.dll',('ModuleLight','ModuleRCSFX','ModuleEnginesFX')),('UnityEngine.CoreModule.dll',('LightType',))]:
 pe=dnfile.dnPE(str(base/dll))
 for t in pe.net.mdtables.TypeDef:
  if str(t.TypeName) in names:
   print(t.TypeName,'methods',[str(x.row.Name) for x in t.MethodList]);print('fields',[str(x.row.Name) for x in t.FieldList])
