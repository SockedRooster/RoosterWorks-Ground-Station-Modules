using System;
using System.Collections.Generic;
using UnityEngine;

// Shapes only the moving support hardware. Hulls, mounting saddles, hatch and
// docking nodes stay fixed. Private mesh instances never modify KSP prefabs.
internal sealed class RWGroundFit
{
    private sealed class Skin
    {public MeshFilter filter;public Mesh original,mesh;public Vector3[] rest,work,rootPoints;public Matrix4x4 rootToMesh;}
    private sealed class Box
    {public BoxCollider box;public Vector3 center,size,rootPoint;public Quaternion rotation;}
    private readonly Transform root;
    private readonly bool stairs;
    private readonly List<Skin> skins=new List<Skin>();
    private readonly List<Box> boxes=new List<Box>();
    public Vector3 toe;
    private float bottom, previous=0f;
    // Stay in the support's local hierarchy. A world-space round trip can
    // round adjacent pad vertices to the same point during vessel loading.
    private Matrix4x4 ToRoot(Transform child)
    {
        Matrix4x4 result=Matrix4x4.identity;
        while(child!=root)
        {
            result=Matrix4x4.TRS(child.localPosition,child.localRotation,child.localScale)*result;
            child=child.parent;
        }
        return result;
    }
    public RWGroundFit(Transform value,bool isStairs)
    {
        root=value;stairs=isStairs;bottom=float.PositiveInfinity;
        foreach(MeshFilter f in root.GetComponentsInChildren<MeshFilter>(true))
        {
            if(f.sharedMesh==null||!f.sharedMesh.isReadable)continue;
            Mesh original=f.sharedMesh;
            Mesh mesh=UnityEngine.Object.Instantiate(original);
            f.sharedMesh=mesh;
            var s=new Skin{mesh=mesh,original=original,filter=f,rest=mesh.vertices};
            Matrix4x4 local=ToRoot(f.transform);
            s.rootToMesh=local.inverse;
            s.work=new Vector3[s.rest.Length];s.rootPoints=new Vector3[s.rest.Length];
            for(int i=0;i<s.rest.Length;i++)s.rootPoints[i]=local.MultiplyPoint3x4(s.rest[i]);
            skins.Add(s);
        }
        foreach(BoxCollider c in root.GetComponentsInChildren<BoxCollider>(true))
        {
            if(c.isTrigger)continue; // Board/grab zone belongs to the landing.
            Vector3 p=ToRoot(c.transform).MultiplyPoint3x4(c.center);
            boxes.Add(new Box{box=c,center=c.center,size=c.size,rootPoint=p,rotation=c.transform.localRotation});
            float y=p.y-c.size.y*.5f;
            if(y<bottom){bottom=y;toe=new Vector3(p.x,y,p.z);}
        }
        if(stairs)toe.x=0;
    }
    public bool Valid{get{return boxes.Count>0&&skins.Count>0;}}
    // Lower foot/pad moves rigidly; only the telescopic transition changes
    // length. The upper sleeve and hull attachment retain their exact shape.
    public static float LegWeight(float y,float lowest)
    {return Mathf.Clamp01((lowest+.85f-y)/.50f);}
    private Vector3 Deform(Vector3 p,float value)
    {
        if(!stairs)return p+Vector3.up*(value*LegWeight(p.y,bottom));
        float w=Mathf.Clamp01((p.z-.20f)/.20f);
        Vector3 pivot=new Vector3(0,-.05f,.20f);
        return Vector3.Lerp(p,pivot+Quaternion.Euler(value,0,0)*(p-pivot),w);
    }
    public void Apply(float value)
    {
        if(value==previous || (value!=0f && Mathf.Abs(value-previous)<.0015f))return;
        previous=value;
        foreach(Skin s in skins)
        {
            for(int i=0;i<s.work.Length;i++)
            {
                Vector3 p=s.rootPoints[i];
                s.work[i]=s.rest[i]+s.rootToMesh.MultiplyVector(Deform(p,value)-p);
            }
            s.mesh.vertices=s.work;
            // Translating the pad and lengthening the leg shaft preserve their
            // authored shading. Stairs change their pitch as they fit terrain.
            if(stairs && value!=0f)s.mesh.RecalculateNormals();
            else if(stairs)s.mesh.normals=s.original.normals;
            s.mesh.RecalculateBounds();
        }
        foreach(Box b in boxes)
        {
            if(b.box==null)continue;
            // Centers are transformed with exactly the same deformation as
            // the visible mesh; upper sleeves stay put, foot pads stay rigid.
            if(stairs)
                b.box.transform.localRotation=b.rotation*Quaternion.Euler(value*Mathf.Clamp01((b.rootPoint.z-.20f)/.20f),0,0);
            else
            {
                float half=b.size.y*.5f;
                float height=Deform(b.rootPoint+Vector3.up*half,value).y-Deform(b.rootPoint-Vector3.up*half,value).y;
                b.box.size=new Vector3(b.size.x,Mathf.Max(.02f,height),b.size.z);
            }
            b.box.center=ToRoot(b.box.transform).inverse.MultiplyPoint3x4(Deform(b.rootPoint,value));
        }
    }
    public Vector3 WorldToe(float value)
    {return root.TransformPoint(Deform(toe,value));}
    public void Dispose()
    {
        foreach(Skin s in skins)
        {
            if(s.filter!=null && s.filter.sharedMesh==s.mesh)s.filter.sharedMesh=s.original;
            if(s.mesh!=null)UnityEngine.Object.Destroy(s.mesh);
        }
        foreach(Box b in boxes)if(b.box!=null)
        {
            b.box.transform.localRotation=b.rotation;
            b.box.center=b.center;
            b.box.size=b.size;
        }
    }
}

internal static class RWGroundSurface
{
    private static readonly RaycastHit[] hits=new RaycastHit[128];
    public static bool Below(Vector3 point,Vector3 up,out Vector3 surface)
    {
        surface=point;
        int count=Physics.RaycastNonAlloc(point+up*1.2f,-up,hits,3f,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore);
        if(count==hits.Length)return false; // Never choose from a truncated set.
        float nearest=float.PositiveInfinity;
        for(int i=0;i<count;i++)
        {
            Collider c=hits[i].collider;
            if(c==null||c.GetComponentInParent<Part>()!=null||c.attachedRigidbody!=null||Vector3.Dot(hits[i].normal,up)<.5f)continue;
            if(hits[i].distance<nearest){nearest=hits[i].distance;surface=hits[i].point;}
        }
        return !float.IsPositiveInfinity(nearest);
    }
}
