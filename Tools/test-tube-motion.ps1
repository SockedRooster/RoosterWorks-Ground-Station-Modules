$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/CollapsibleTube.cs') -Raw
$doubles=Get-Content (Join-Path $kit 'Tools/TubeMotionDoubles.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/TubeMotionTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$doubles+"`n"+$tests)
[TubeMotionTest]::Run()
