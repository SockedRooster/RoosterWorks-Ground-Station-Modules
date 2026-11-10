"""Independent native/CFG/dependency/scope/preservation checks for the hot patch."""
from pathlib import Path
import sys,json,hashlib,math,re
from collections import Counter
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];W=R.parent;CORE=W/'rw-v075dev5'
sys.path[:0]=[str(CORE/'Source'),str(CORE/'Tools')]
from config_nodes import parse,dump
from native_model import load,walk
GD=R/'GameData/RoosterWorksGroundModules'
roles=('HAB','LAB','CMD','LOG','GRN','AIR','PWR','HUB','TUB','ELB');ids={'RW_GND_'+r for r in roles};models={}
for role in roles:
    name='RW_GND_'+role;model=load(GD/f'Models/{name}.mu');models[name]=model
    nodes=[n for _,n in walk(model.root)];report=json.loads((R/f'Reports/{name}.json').read_text())
    assert report['source_blend_sha256']==hashlib.sha256((W/f'ground-modules-art-v4/Models/{name}.blend').read_bytes()).hexdigest()
    assert len(model.materials)==1+max(i for n in nodes for i in n.get('materials',[]))
    visual=[n['mesh'] for n in nodes if 'mesh' in n];assert sum(len(t) for m in visual for t in m['submeshes'])==report['triangles']
    for mesh in visual:
        assert len(mesh['vertices'])<65535 and len(mesh['vertices'])==len(mesh['uvs'])==len(mesh['normals'])
        v=np.array(mesh['vertices']);norm=np.array(mesh['normals']);assert np.isfinite(v).all() and np.allclose(np.linalg.norm(norm,axis=1),1,atol=2e-5)
        t=np.array(mesh['submeshes'][0]);cross=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);dots=(cross*norm[t].mean(axis=1)).sum(axis=1)
        assert (dots < -1e-6).sum()==0,('Inward face/normal mismatch',name,int((dots < -1e-6).sum()))
    for texture in model.textures:
        assert '/' not in texture['name'] and '\\' not in texture['name'],'MU texture name must be relative to its model directory'
        p=GD/'Models'/(texture['name'].rsplit('/',1)[-1]+'.png');assert p.is_file();Image.open(p).verify()
    solids=[n for n in nodes if 'collider' in n and not n['collider']['trigger']];assert solids and report['legs']>=4
    for n in solids:
        c=n['collider']
        if c['type']=='box':assert all(x>0 for x in c['size']);continue
        assert c['convex']==1
        mesh=c['mesh'];assert sum(len(t) for t in mesh['submeshes'])<=255
        edges=Counter()
        for triangles in mesh['submeshes']:
            for t in triangles:
                pts=[tuple(round(v,5) for v in mesh['vertices'][i]) for i in t]
                for a,b in zip(pts,pts[1:]+pts[:1]):edges[tuple(sorted((a,b)))]+=1
        assert set(edges.values())=={2},('Open collision hull',name,n['name'])
    tags={n['tag'] for n in nodes if n.get('collider',{}).get('trigger')}
    assert tags==({'Airlock','Ladder'} if role in ('HAB','LAB','CMD','AIR') else set())
    for n in nodes:
        if n['tag'] in ('Airlock','Ladder'):assert n['layer']==21 and n['rotation']==((0,1,0,0) if n['tag']=='Ladder' else (0,0,0,1))
    part=parse((GD/f'Parts/{name}.cfg').read_text()).children[0]
    assert part.header=='PART:NEEDS[RoosterWorksStationModules]' and part.get('name')==name and part.get('rescaleFactor')=='1'
    assert next(n for n in part.children if n.header=='MODEL').get('model')==f'RoosterWorksGroundModules/Models/{name}'
    assert part.get('vesselType')=='Base' and float(part.get('mass'))>0
    motion=[n for n in part.children if n.get('name')=='ModuleRWGroundDeploy'];assert {n.get('deploymentID') for n in motion}==({'Legs','Stairs'} if role in ('HAB','LAB','CMD','AIR') else {'Legs'})
    lookup={n['name']:n for n in nodes}
    for module in motion:
        specs=module.children;assert len(specs)==(report['legs'] if module.get('deploymentID')=='Legs' else 1)
        for spec in specs:
            root=lookup[spec.get('name')];assert root['children'] and any('mesh' in n for _,n in walk(root)) and any('collider' in n for _,n in walk(root))
    if role in ('HAB','LAB','CMD'):
        glass=np.array([v for n in nodes if 'mesh' in n and any(model.materials[i]['name']=='RW_Ground_glass' for i in n.get('materials',[])) for v in n['mesh']['vertices']])
        assert glass[:,1].min()>.40,('Window remained beneath hull/door',name,glass[:,1].min())
    assert report['label_triangles_removed']>0
    if role=='CMD':assert report['dish_backfaces']>0
    old='RW_ADP_250_375' if role=='ADP' else f'RW_{role}_250'
    baseline=parse((CORE/f'GameData/RoosterWorksStationModules/Parts/{old}.cfg').read_text()).children[0]
    if role=='HUB':
        baseline=parse((CORE/'GameData/RoosterWorksStationModules/Parts/RW_CUP_250.cfg').read_text()).children[0]
        assert part.get('CrewCapacity')=='1' and next(n for n in part.children if n.header=='INTERNAL').get('name')=='cupolaInternal'
        assert next(n for n in part.children if n.header=='INTERNAL').get('offset')=='0, 2, 0'
        donor=load(CORE/'GameData/RoosterWorksStationModules/Models/RW_CUP_250.mu')
        def glass_bounds(m):
            v=np.array([v for _,n in walk(m.root) if 'mesh' in n and not n['name'].startswith('RW_EndWindows') and any('glass' in m.materials[i]['name'].lower() for i in n.get('materials',[])) for v in n['mesh']['vertices']]);return np.array([v.min(0),v.max(0)])
        assert np.allclose(glass_bounds(model)-glass_bounds(donor),(0,2,0),atol=1e-5),'IVA shift differs from observation glass shift'
        stack={k:v for k,v in part.values if k.startswith('node_stack_')};assert set(stack)=={'node_stack_right','node_stack_left','node_stack_front','node_stack_back'}
        assert all(float(v.split(',')[1])==0 and float(v.split(',')[4])==0 for v in stack.values())
        assert {'GroundHubClosedHull','GroundHubObservationHull'}<={n['name'] for n in solids}
        assert all(not n['name'].startswith('Hull_') for n in solids),'Obsolete six-port collision was retained'
    elif role=='CMD':assert part.get('CrewCapacity')=='3' and next(n for n in part.children if n.header=='INTERNAL').get('name')=='Mk1-3'
    else:assert part.get('CrewCapacity')==baseline.get('CrewCapacity')
    assert [dump(n) for n in part.children if n.header=='RESOURCE']==[dump(n) for n in baseline.children if n.header=='RESOURCE'],('Base resource balance changed',name)
    assert all(n.get('name') not in ('ModuleRWStationHatch','ModulePartVariants') for n in part.children if n.header=='MODULE')
    for n in part.children:
        if n.header=='MODULE' and n.get('name')=='ModuleColorChanger':
            renderers={x['name'] for x in nodes if 'mesh' in x}
            included=[v for k,v in n.values if k=='includedRenderer'];assert included and set(included)<=renderers
        if n.header=='MODULE' and n.get('name')=='ModuleLight':assert n.get('lightName') in {x['name'] for x in nodes if 'light' in x}
    print('PASS native/config',name,report['triangles'],'triangles,',report['legs'],'supports,',report['stairs'],'steps',flush=True)
assert len(list((GD/'Parts').glob('*.cfg')))==13
assert {p.stem for p in (GD/'Models').glob('*.mu')}==ids|{'RW_GND_END_250_125','RW_GND_FLEX','RW_GND_VT'}
hubhab=parse((GD/'Compatibility/CupolaKerbalism.cfg').read_text()).children[-1].children[0]
assert hubhab.get('%volume')=='16.2' and hubhab.get('%surface')=='52'
for path in (GD/'Compatibility').glob('*.cfg'):
    if path.name=='FlexRingGeometry.cfg':continue # Dedicated flex validation handles moving parents and legless hull.
    if path.name.startswith('Endcap'):continue # Dedicated endcap validation covers its new scoped maps.
    if path.name=='SkycraneEndcapCarrier.cfg':
        rule=parse(path.read_text()).children
        assert len(rule)==1 and rule[0].header=='@PART[RW_SC_CARRIER_090]:NEEDS[RoosterWorksSkycrane]:AFTER[RoosterWorksSkycrane]'
        assert len(rule[0].children)==1 and rule[0].children[0].header=='@MODULE[ModuleDockingNode]'
        assert rule[0].children[0].values==[('@nodeType','size1')]
        continue # Exact optional companion-carrier compatibility, no broad selectors.
    for n in parse(path.read_text()).children:
        assert ':FOR[RoosterWorksStationModules]' not in n.header,'Hot patch falsely advertises the core dependency'
        if n.header.startswith('@PART['):
            selector=n.header.split(']',1)[0][6:];assert set(selector.split(','))<=ids,('Mutates non-ground part',path,selector)
        else:assert n.header=='RW_RING_MAP' and n.get('model') in ids,('Global definition unexpectedly copied',path,n.header)
elbow=parse((GD/'Parts/RW_GND_ELB.cfg').read_text()).children[0]
a=[float(x) for x in elbow.get('node_stack_top').split(',')];b=[float(x) for x in elbow.get('node_stack_bottom').split(',')]
assert a[1]==b[1]==0 and np.isclose(np.dot(a[3:6],b[3:6]),0)
for k in ('node_stack_top','node_stack_bottom'):
    v=[float(x) for x in parse((GD/'Parts/RW_GND_TUB.cfg').read_text()).children[0].get(k).split(',')];assert v[1]==0
ringmaps=parse((GD/'Compatibility/GroundRingGeometry.cfg').read_text()).children;assert {n.get('model') for n in ringmaps}==ids
for entry in ringmaps:
    lookup=dict(walk(models[entry.get('model')].root))
    for spec in entry.children:
        node=lookup[spec.get('path')];mesh=node['mesh'];assert len(mesh['vertices'])==int(spec.get('vertices'))
        selected=set()
        for s in spec.get('ranges').split(','):
            start,count=map(int,s.split(':'));assert start>=0 and count>0 and start+count<=len(mesh['submeshes'][0]);keys=set(range(start,start+count));assert not keys&selected;selected|=keys
        for color in ('steel','white','charcoal','blue','green','red','gold'):assert (CORE/f'GameData/RoosterWorksStationModules/Models/rwm_ring_{spec.get("texture")}_{color}.png').is_file()
cmd=parse((GD/'Compatibility/ZZZCommandStorage075.cfg').read_text()).children[0].children[0]
lab=parse((GD/'Compatibility/ZZZScienceStorage075.cfg').read_text()).children[0].children[0]
assert cmd.get('%dataCapacity')=='200' and cmd.get('%maxDataCapacityFactor')=='5'
assert lab.get('%dataCapacity')=='250' or float(lab.get('%dataCapacity'))==250
assert lab.get('%maxDataCapacityFactor')=='10' and lab.get('%sampleCapacity')=='10' and lab.get('%maxSampleCapacityFactor')=='10'
power=parse((GD/'Compatibility/PowerVariants.cfg').read_text()).children[0]
controller=next(n for n in power.children if n.get('name')=='ModuleRWPowerVariant')
assert controller.get('batteryCapacity')=='2980' and controller.get('reactorCapacity')=='2450'
assert (GD/'Compatibility/LogisticsLoadouts.cfg').is_file() and (GD/'Compatibility/GreenhouseKerbalism.cfg').is_file()
for path,digest in json.loads((R/'Reports/READ_ONLY_INPUTS.json').read_text()).items():
    assert hashlib.sha256((W/path).read_bytes()).hexdigest()==digest,('Existing file changed',path)
for line in (R/'CHECKSUMS-SHA256.txt').read_text().splitlines():
    digest,path=line.split('  ',1);assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('PASS ten scoped additive parts; four-port observation hub and revised collision; level elbow; science/command tiers, reactor variants, loadouts, greenhouse, lighting, ring maps; all read-only inputs unchanged; GameData manifest')
