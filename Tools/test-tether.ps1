$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/GroundTether.cs') -Raw
$doubles=Get-Content (Join-Path $kit 'Tools/TetherTestDoubles.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/TetherTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$doubles+"`n"+$tests)
[TetherTest]::Run()
