from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'work/python-deps'))
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
pe=dnfile.dnPE('D:/SteamLibrary/steamapps/common/Kerbal Space Program/KSP_x64_Data/Managed/Assembly-CSharp.dll')
for t in pe.net.mdtables.TypeDef:
 name=str(t.TypeName)
 if name not in ('PartJoint','ModuleDockingNode','Part','Vessel'):continue
 fields=[(str(f.row.Name),'public' if f.row.Flags.fdPublic else 'private',f.row.Signature.value.hex()) for f in t.FieldList]
 methods=[str(m.row.Name) for m in t.MethodList]
 if name=='Part':fields=[f for f in fields if any(k in f[0].lower() for k in ('attpos','orgpos','joint','parent','children'))];methods=[m for m in methods if any(k in m.lower() for k in ('position','joint','attach'))]
 if name=='Vessel':fields=[];methods=[m for m in methods if any(k in m.lower() for k in ('position','joint','structure'))]
 if name=='ModuleDockingNode':fields=[f for f in fields if any(k in f[0].lower() for k in ('joint','othernode','dockedpart'))];methods=[]
 print(name,'FIELDS',fields,'METHODS',methods)
 if name=='PartJoint':
  for item in t.MethodList:
   if str(item.row.Name) not in ('SetupJoint','OnPartUnpack','OnPartPack'):continue
   print('IL',item.row.Name)
   for ins in read_method_body_from_bytes(pe.get_data(item.row.Rva,100000)).instructions:
    tok=ins.operand;value=str(tok)
    if hasattr(tok,'table') and tok.table==4:value=str(pe.net.mdtables.Field[tok.rid-1].Name)
    if hasattr(tok,'table') and tok.table==10:value=str(pe.net.mdtables.MemberRef[tok.rid-1].Name)
    if hasattr(tok,'table') and tok.table==6:value=str(pe.net.mdtables.MethodDef[tok.rid-1].Name)
    print(ins.offset,ins.opcode,value)
rows=json.loads((R/'Reports/LAYOUT_INVENTORY.json').read_text())['CMD']
for r in rows:
 if any(k in r['name'].lower() for k in ('dish','antenna','radiator','roof heat','receiver','feed','mast')):print('ART',r)
