$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/ExteriorLight.cs') -Raw
$release=Get-Content (Join-Path $kit 'Source/PodRelease.cs') -Raw
$harness=(Get-Content (Join-Path $kit 'Tools/LightingReleaseTests.cs') -Raw).Replace('using System;','').Replace('using System.Collections.Generic;','')
Add-Type -TypeDefinition ("using System;`n"+$source+"`n"+$release+"`n"+$harness)
[LightingReleaseTest]::Run()
