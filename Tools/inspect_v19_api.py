from pathlib import Path
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'work/python-deps'))
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
pe=dnfile.dnPE('D:/SteamLibrary/steamapps/common/Kerbal Space Program/KSP_x64_Data/Managed/Assembly-CSharp.dll')
def operand(tok):
 if hasattr(tok,'table'):
  if tok.table==4:return str(pe.net.mdtables.Field[tok.rid-1].Name)
  if tok.table==6:return str(pe.net.mdtables.MethodDef[tok.rid-1].Name)
  if tok.table==10:return str(pe.net.mdtables.MemberRef[tok.rid-1].Name)
  if tok.table==0x70:return str(pe.net.user_strings.get(tok.rid))
 return str(tok)
targets={'ModuleLight':('.ctor','OnStart','FixedUpdate','LightsOn','SetLightState','SetEmission'),'ModuleDecouple':('.ctor','OnStart','Decouple'),'ModuleAnchoredDecoupler':('.ctor','OnStart','Decouple'),'Part':('FindModelTransform',),'ModuleRCS':()}
for t in pe.net.mdtables.TypeDef:
 name=str(t.TypeName)
 if name not in targets:continue
 print('TYPE',name,'FIELDS',[(str(f.row.Name),f.row.Signature.value.hex()) for f in t.FieldList])
 for m in t.MethodList:
  if str(m.row.Name) not in targets[name] or not m.row.Rva:continue
  print('METHOD',name,str(m.row.Name))
  for ins in read_method_body_from_bytes(pe.get_data(m.row.Rva,100000)).instructions:print(ins.offset,ins.opcode,operand(ins.operand))
