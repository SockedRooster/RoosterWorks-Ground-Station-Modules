$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/GroundDocking.cs') -Raw
$doubles=Get-Content (Join-Path $kit 'Tools/DockingTestDoubles.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/DockingTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$doubles+"`n"+$tests)
[DockingTest]::Run()