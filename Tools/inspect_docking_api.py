from pathlib import Path
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'work/python-deps'))
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
files=[Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/KSP_x64_Data/Managed/Assembly-CSharp.dll')]
files+=list(Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/DockingPortAlignmentIndicator').rglob('*Named*.dll'))
files+=list(Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/DockingPortNamed').rglob('*.dll'))
files+=list(Path('D:/SteamLibrary/steamapps/common/Kerbal Space Program/GameData/NavyFish').rglob('ModuleDockingNodeNamed.dll'))
for file in files:
 pe=dnfile.dnPE(str(file))
 for t in pe.net.mdtables.TypeDef:
  name=str(t.TypeName)
  if name not in ('ModuleDockingNode','ModuleCommand','Part','AttachNode','PartModule','BaseField','ModuleDockingNodeNamed'):continue
  fields=[(str(f.row.Name),'public' if f.row.Flags.fdPublic else 'private',f.row.Signature.value.hex()) for f in t.FieldList]
  methods=[str(m.row.Name) for m in t.MethodList]
  if name in ('Part','PartModule','BaseField'):fields=[f for f in fields if any(k in f[0].lower() for k in ('module','info','name','title'))];methods=[m for m in methods if any(k in m.lower() for k in ('attachnode','reference'))]
  print(name,'FIELDS',fields,'METHODS',methods)
  if name=='ModuleDockingNode':
   for item in t.MethodList:
    if str(item.row.Name)!='.ctor':continue
    body=read_method_body_from_bytes(pe.get_data(item.row.Rva,50000))
    for i,ins in enumerate(body.instructions):
     tok=ins.operand
     if str(ins.opcode)=='stfld' and tok.table==4:
      field=str(pe.net.mdtables.Field[tok.rid-1].Name)
      if any(s in field for s in ('acquire','capture','Distance','Ejection')):print('DEFAULT',field,str(body.instructions[i-1].opcode),body.instructions[i-1].operand)
