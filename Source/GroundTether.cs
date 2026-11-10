using System;
using System.Collections.Generic;
using UnityEngine;

// Command-controlled anchoring for every connected RoosterWorks ground body.
// Temporary per-module joints preserve the settled assembly's current shape;
// no module is teleported and no unrelated mod's physics anchors are modified.
public sealed class ModuleRWGroundTether : PartModule
{
    [KSPField(isPersistant = true)] public bool tetherEnabled;
    [KSPField] public float settleSeconds = 1.5f;
    [KSPField] public float engageSpeed = .15f;
    [KSPField] public float releaseSpeed = .75f;
    [KSPField(guiActive = true, guiName = "Ground tether")]
    public string tetherStatus = "Off";
    private sealed class Anchor
    {
        public Part part;
        public Rigidbody body, proxy;
        public GameObject owner;
        public FixedJoint joint;
        public double latitude, longitude, altitude;
        public Quaternion relativeRotation;
    }
    private readonly List<Anchor> anchors = new List<Anchor>();
    private Vessel attachedVessel;
    private CelestialBody attachedBody;
    private int attachedPartCount, recoveryAttempts;
    private float settled, stableTime;
    private bool subscribed;

    public override void OnStart(StartState state)
    {
        base.OnStart(state);
        if (!HighLogic.LoadedSceneIsFlight) return;
        GameEvents.onVesselGoOnRails.Add(OnRails);
        GameEvents.onFloatingOriginShift.Add(OnOriginShift);
        subscribed = true;
        Refresh(tetherEnabled ? "Waiting for stable ground" : "Off");
    }
    [KSPEvent(guiActive = true, guiActiveUnfocused = true, externalToEVAOnly = true,
        unfocusedRange = 5f, guiName = "Enable Ground Tether")]
    public void EnableTether() { SetEnabled(true, "Waiting for stable ground"); }
    [KSPEvent(guiActive = true, guiActiveUnfocused = true, externalToEVAOnly = true,
        unfocusedRange = 5f, guiName = "Release Ground Tether")]
    public void DisableTether() { SetEnabled(false, "Off"); }
    [KSPAction("Enable Ground Tether")] public void EnableAction(KSPActionParam p) { EnableTether(); }
    [KSPAction("Release Ground Tether")] public void ReleaseAction(KSPActionParam p) { DisableTether(); }
    [KSPAction("Toggle Ground Tether")] public void ToggleAction(KSPActionParam p)
    { SetEnabled(!tetherEnabled, tetherEnabled ? "Off" : "Waiting for stable ground"); }
    private void Refresh(string status)
    {
        tetherStatus = status;
        Events["EnableTether"].active = !tetherEnabled;
        Events["DisableTether"].active = tetherEnabled;
    }
    private void SetEnabled(bool value, string status)
    {
        if (vessel == null) { ClearAnchors(); tetherEnabled = value; recoveryAttempts = 0; Refresh(status); return; }
        foreach (ModuleRWGroundTether module in vessel.FindPartModulesImplementing<ModuleRWGroundTether>())
        { module.ClearAnchors(); module.tetherEnabled = value; module.recoveryAttempts = 0; module.Refresh(status); }
    }
    public static void ReleaseForVessel(Vessel target, string reason)
    {
        if (target == null) return;
        foreach (ModuleRWGroundTether module in target.FindPartModulesImplementing<ModuleRWGroundTether>())
        { module.ClearAnchors(); module.tetherEnabled = false; module.recoveryAttempts = 0; module.Refresh(reason); }
    }
    private bool Leader()
    {
        foreach (ModuleRWGroundTether module in vessel.FindPartModulesImplementing<ModuleRWGroundTether>())
            if (module.tetherEnabled) return module == this;
        return false;
    }
    private bool SupportsReady()
    {
        bool found = false;
        foreach (ModuleRWGroundDeploy module in vessel.FindPartModulesImplementing<ModuleRWGroundDeploy>())
            if (module.deploymentID == "Legs")
            { found = true; if (!module.deployed || module.deployment < .99999f) return false; }
        return found;
    }
    private List<Part> Targets()
    {
        var result = new List<Part>();
        foreach (Part p in vessel.parts)
            if (p != null && p.partInfo != null && p.partInfo.name != null &&
                // KSP normalizes underscores to dots in loaded part names.
                // Keep raw config names supported for prefabs and tooling.
                (p.partInfo.name.StartsWith("RW_GND_", StringComparison.Ordinal) ||
                 p.partInfo.name.StartsWith("RW.GND.", StringComparison.Ordinal))) result.Add(p);
        return result;
    }
    private bool SameAssembly(List<Part> targets)
    {
        if (attachedVessel != vessel || attachedBody != vessel.mainBody || attachedPartCount != vessel.parts.Count) return false;
        foreach (Anchor a in anchors)
            if (a.part == null || a.part.vessel != vessel || !targets.Contains(a.part) || a.body != a.part.Rigidbody) return false;
        var bodies = new HashSet<Rigidbody>();
        foreach (Part p in targets) if (p.Rigidbody != null) bodies.Add(p.Rigidbody);
        return bodies.Count == anchors.Count;
    }
    // Derive orientation from KSP's actual celestial-frame position API. The
    // rendered planet Transform can differ from that frame; mixing them can
    // create a spurious rotation/load as physics begins.
    private static Quaternion SurfaceRotation(CelestialBody body, double lat, double lon, double alt)
    {
        Vector3d p = body.GetWorldSurfacePosition(lat, lon, alt);
        Vector3 up = (Vector3)(body.GetWorldSurfacePosition(lat, lon, alt + 1) - p);
        double delta = lat > 89.9 ? -.01 : .01;
        Vector3 north = (Vector3)(body.GetWorldSurfacePosition(lat + delta, lon, alt) - p);
        if (delta < 0) north = -north;
        north = Vector3.ProjectOnPlane(north, up);
        return Quaternion.LookRotation(north.normalized, up.normalized);
    }
    public void FixedUpdate()
    {
        if (!HighLogic.LoadedSceneIsFlight || part == null || vessel == null) { ClearAnchors(); return; }
        if (!tetherEnabled) { ClearAnchors(); return; }
        if (!Leader()) { ClearAnchors(); Refresh("Controlled by connected command station"); return; }
        foreach (ModuleRWGroundTether module in vessel.FindPartModulesImplementing<ModuleRWGroundTether>())
            if (!module.tetherEnabled) { module.tetherEnabled = true; module.Refresh("Controlled by connected command station"); }
        if (!vessel.loaded || vessel.packed || TimeWarp.CurrentRateIndex != 0)
        { ClearAnchors(); Refresh("Suspended during time warp / loading"); return; }
        if (vessel.precalc != null && vessel.precalc.isEasingGravity)
        { ClearAnchors(); Refresh("Waiting for ground physics"); return; }
        if (vessel.ctrlState != null && (vessel.ctrlState.mainThrottle > .01f || Math.Abs(vessel.ctrlState.wheelThrottle) > .01f))
        { ReleaseForVessel(vessel, "Released for movement controls"); return; }
        if (!SupportsReady()) { ReleaseForVessel(vessel, "Released: lower support legs first"); return; }
        if (!vessel.Landed || vessel.Splashed || vessel.mainBody == null)
        {
            if (anchors.Count > 0) ReleaseForVessel(vessel, "Released: no longer landed");
            else { settled = 0; Refresh("Waiting to land"); }
            return;
        }
        double speed = vessel.srf_velocity.magnitude;
        if (double.IsNaN(speed) || double.IsInfinity(speed) || speed > Math.Max(.3f, releaseSpeed))
        { ReleaseForVessel(vessel, "Released: base is moving"); return; }
        List<Part> targets = Targets();
        if (targets.Count == 0) { ClearAnchors(); Refresh("Waiting for connected ground modules"); return; }
        foreach (Part p in targets)
            if (p.Rigidbody == null || p.Rigidbody.isKinematic)
            { ClearAnchors(); Refresh("Waiting for module physics"); return; }
        if (anchors.Count > 0 && !SameAssembly(targets))
        { ClearAnchors(); recoveryAttempts = 0; Refresh("Waiting after assembly change"); return; }
        if (anchors.Count > 0)
        {
            foreach (Anchor a in anchors)
                if (a.joint == null || a.proxy == null)
                {
                    ClearAnchors(); recoveryAttempts++;
                    if (recoveryAttempts > 3) ReleaseForVessel(vessel, "Released: tether could not stabilize");
                    else Refresh("Recovering ground tether (" + recoveryAttempts + "/3)");
                    return;
                }
            foreach (Anchor a in anchors)
            {
                a.proxy.MovePosition(attachedBody.GetWorldSurfacePosition(a.latitude, a.longitude, a.altitude));
                a.proxy.MoveRotation(SurfaceRotation(attachedBody, a.latitude, a.longitude, a.altitude) * a.relativeRotation);
                SetStrength(a, anchors.Count);
            }
            stableTime += Time.fixedDeltaTime;
            if (stableTime >= 15f) recoveryAttempts = 0;
            Refresh("Engaged: " + targets.Count + "/" + targets.Count + " modules"); return;
        }
        // Wait for every module's body, not just the command station. A shared
        // Rigidbody is anchored once, avoiding duplicate constraints.
        foreach (Part p in targets)
            if (p.Rigidbody == null || p.Rigidbody.isKinematic)
            { settled = 0; Refresh("Waiting for module physics"); return; }
        if (speed > Math.Max(.01f, Math.Min(.3f, engageSpeed)))
        { settled = 0; Refresh("Waiting for base to stop"); return; }
        settled += Time.fixedDeltaTime;
        if (settled < Math.Max(.5f, settleSeconds)) { Refresh("Settling connected modules"); return; }
        CreateAnchors(targets);
    }
    private void SetStrength(Anchor a, int count)
    {
        float gravity = (float)vessel.graviticAcceleration.magnitude;
        float ownWeight = a.body.mass * gravity;
        float sharedWeight = vessel.GetTotalMass() * gravity / Math.Max(1, count);
        a.joint.breakForce = Math.Max(1000f, Math.Max(ownWeight * 25f, sharedWeight * 12f));
        a.joint.breakTorque = a.joint.breakForce * 3f;
    }
    private void CreateAnchors(List<Part> targets)
    {
        attachedVessel = vessel; attachedBody = vessel.mainBody; attachedPartCount = vessel.parts.Count;
        var bodies = new HashSet<Rigidbody>();
        try
        {
            foreach (Part p in targets)
            {
                Rigidbody rb = p.Rigidbody; if (!bodies.Add(rb)) continue;
                Vector3 position = rb.worldCenterOfMass;
                var a = new Anchor { part = p, body = rb };
                anchors.Add(a); // Register ownership before allocating for exception cleanup.
                a.latitude = attachedBody.GetLatitude(position, false);
                a.longitude = attachedBody.GetLongitude(position, false);
                a.altitude = attachedBody.GetAltitude(position);
                a.relativeRotation = Quaternion.Inverse(SurfaceRotation(attachedBody, a.latitude, a.longitude, a.altitude)) * rb.rotation;
                a.owner = new GameObject("RW Ground Tether / " + p.flightID);
                a.owner.transform.position = position; a.owner.transform.rotation = rb.rotation;
                a.proxy = a.owner.AddComponent<Rigidbody>(); a.proxy.isKinematic = true; a.proxy.useGravity = false;
                a.joint = rb.gameObject.AddComponent<FixedJoint>();
                a.joint.autoConfigureConnectedAnchor = false;
                a.joint.anchor = rb.transform.InverseTransformPoint(position);
                a.joint.connectedAnchor = Vector3.zero; a.joint.connectedBody = a.proxy;
                a.joint.enableCollision = false; a.joint.enablePreprocessing = false;
                SetStrength(a, targets.Count);
            }
            stableTime = 0; Refresh("Engaged: " + targets.Count + "/" + targets.Count + " modules");
        }
        catch (Exception e)
        { ClearAnchors(); ReleaseForVessel(vessel, "Released: module physics unavailable"); Debug.LogError("[RoosterWorks Ground] Tether setup: " + e.Message); }
    }
    private void ClearAnchors()
    {
        foreach (Anchor a in anchors)
        {
            if (a.joint != null) UnityEngine.Object.Destroy(a.joint);
            if (a.owner != null) UnityEngine.Object.Destroy(a.owner);
        }
        anchors.Clear(); attachedVessel = null; attachedBody = null; settled = 0; stableTime = 0;
    }
    private void OnRails(Vessel target)
    {
        if (target == vessel || target == attachedVessel)
        { ClearAnchors(); Refresh(tetherEnabled ? "Suspended during time warp / loading" : "Off"); }
    }
    private void OnOriginShift(Vector3d offset, Vector3d velocity)
    { ClearAnchors(); if (tetherEnabled) Refresh("Waiting after reference-frame shift"); }
    public void OnDestroy()
    {
        if (subscribed) { GameEvents.onVesselGoOnRails.Remove(OnRails); GameEvents.onFloatingOriginShift.Remove(OnOriginShift); }
        ClearAnchors();
    }
    public override string GetInfo()
    { return "Ground tether for all connected RoosterWorks ground modules. Lower all support legs and stop before engaging. One command-station switch anchors every module; releases for leg or launch controls and resumes after time warp or loading."; }
}
