"""Remove the legacy paired hull conduits from the dev.40 Ground Modules meshes."""
import json
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SDK = next((ROOT.parent / "Releases/2026-11-02").glob("*Modules*Source"))
sys.path[:0] = [str(SDK/"Source"), str(SDK/"Tools"), str(SDK/".build-deps")]
from build_ring_options import components
from native_model import load, walk


def strip_runs(path):
    model = load(path)
    raw = path.read_bytes()
    groups = {"rwm_bronze": [], "rwm_graphite": [], "rwm_steel": []}
    meshes = {}
    for _, node in walk(model.root):
        if "mesh" not in node or not node.get("materials"):
            continue
        props = model.materials[node["materials"][0]]["properties"]
        texture = model.textures[props["_MainTex"]["index"]]["name"]
        if texture not in groups:
            continue
        mesh = node["mesh"]
        triangles = np.asarray(mesh["submeshes"][0], dtype="<i4")
        vertices = np.asarray(mesh["vertices"])
        meshes[node["name"]] = (mesh, triangles)
        for rows in components(mesh):
            if len(rows) != 12:
                continue
            pts = vertices[np.unique(triangles[rows])]
            lo, hi = pts.min(0), pts.max(0)
            dx, dy, dz = hi-lo
            if texture == "rwm_steel":
                match = .015 < dx < .03 and .075 < np.hypot(dy,dz) < .1
            else:
                match = dx > .15 and .009 < dy < .016 and .009 < dz < .016
            if match:
                groups[texture].append(((hi+lo)/2, dx, node["name"], rows))
    selected = {}
    def select(item):
        selected.setdefault(item[2], []).extend(item[3])
    for gold in groups["rwm_bronze"]:
        center, length = gold[:2]
        mates = [g for g in groups["rwm_graphite"] if abs(g[1]-length)<.0001
                 and abs(g[0][0]-center[0])<.0001 and .05 < np.linalg.norm(g[0]-center) < .065]
        assert len(mates)==1
        select(gold)
        select(mates[0])
        mid = (mates[0][0]+center)/2
        for x in (mid[0]-length/2,mid[0],mid[0]+length/2):
            clips = [g for g in groups["rwm_steel"] if abs(g[0][0]-x)<.001
                     and np.linalg.norm(g[0][1:]-mid[1:])<.012]
            assert len(clips)==1, (path,x,clips)
            select(clips[0])
    assert len(groups["rwm_bronze"])==len(groups["rwm_graphite"])
    for name, rows in selected.items():
        mesh, triangles = meshes[name]
        assert len(set(rows))==len(rows)
        # Retain indices used by the runtime ring color map.
        original = struct.pack("<ii",19,triangles.size)+triangles.tobytes()
        pos = raw.index(original,raw.index(name.encode()))+8
        triangles[rows] = triangles[rows,0,None]
        raw = raw[:pos]+triangles.tobytes()+raw[pos+triangles.nbytes:]
        mesh["submeshes"][0] = list(map(tuple,triangles.tolist()))
    if selected:
        path.write_bytes(raw)
        assert load(path).root==model.root
    return len(groups["rwm_bronze"]), raw


def build():
    base = next(ROOT.glob("*dev.40-Install.zip"))
    target = base.with_name(base.name.replace("dev.40","dev.41"))
    pending = target.with_suffix(".partial")
    changes = set()
    total = 0
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(pending,"w") as out:
        for entry in old.infolist():
            name = entry.filename
            data = old.read(entry)
            if name.endswith(".mu"):
                path = ROOT/"Build"/"side-conduit-audit.mu"
                path.write_bytes(data)
                count,data = strip_runs(path)
                if count:
                    changes.add(name)
                    total += count
                    print(Path(name).stem,count)
            if name.endswith(".version"):
                info = json.loads(data)
                info["VERSION"]["BUILD"] = 41
                data = (json.dumps(info,indent=2)+"\n").encode()
                changes.add(name)
            out.writestr(entry,data)
    with zipfile.ZipFile(pending) as new, zipfile.ZipFile(base) as old:
        assert total == 48 and len(changes)==10
        assert new.testzip() is None and new.namelist()==old.namelist()
        assert changes=={n for n in old.namelist() if old.read(n)!=new.read(n)}
    pending.replace(target)


if __name__=="__main__":
    build()

