$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$core=Join-Path (Split-Path -Parent $kit) 'rw-v075dev10'
$source="using System.Globalization;`n"+(Get-Content (Join-Path $core 'Source/RingColor.cs') -Raw)
$doubles=Get-Content (Join-Path $kit 'Tools/HardpointColorDoubles.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/HardpointColorTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$doubles+"`n"+$tests)
$fixture=Get-Content (Join-Path $kit 'Reports/HARDPOINT_COLOR_FIXTURE.json') -Raw | ConvertFrom-Json
foreach($spec in $fixture){[HardpointColorTest]::Add($spec.path,$spec.texture,$spec.vertexCount,[int[]]$spec.triangles,$spec.ranges)}
[HardpointColorTest]::Run()
