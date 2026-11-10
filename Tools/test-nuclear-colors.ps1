param([ValidateSet('RW_GND_NST','RW_GND_NSM','RW_GND_CEN')][string]$PartID='RW_GND_NST')
$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$core=Join-Path (Split-Path -Parent $kit) 'rw-v075dev10'
$source="using System.Globalization;`n"+(Get-Content (Join-Path $core 'Source/RingColor.cs') -Raw)
$doubles=Get-Content (Join-Path $kit 'Tools/HardpointColorDoubles.cs') -Raw
$fixture=Get-Content (Join-Path $kit 'Reports/NUCLEAR_COLOR_FIXTURE.json') -Raw | ConvertFrom-Json
$tests=(Get-Content (Join-Path $kit 'Tools/HardpointColorTests.cs') -Raw).Replace('RW_GND_HPT',$PartID)
Add-Type -TypeDefinition ($source+"`n"+$doubles+"`n"+$tests)
foreach($spec in $fixture.$PartID){[HardpointColorTest]::Add($spec.path,$spec.texture,$spec.vertexCount,[int[]]$spec.triangles,$spec.ranges)}
[HardpointColorTest]::Run()
