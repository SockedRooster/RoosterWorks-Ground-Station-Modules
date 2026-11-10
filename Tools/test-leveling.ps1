$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/GroundDeploy.cs') -Raw
$fit=Get-Content (Join-Path $kit 'Source/GroundFit.cs') -Raw
$level=Get-Content (Join-Path $kit 'Source/GroundLevel.cs') -Raw
$fit=$fit -replace '(?m)^using .*;\r?\n',''
$level=$level -replace '(?m)^using .*;\r?\n',''
$doubles=Get-Content (Join-Path $kit 'Tools/LevelingDoubles.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/LevelingTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$fit+"`n"+$level+"`n"+$doubles+"`n"+$tests)
[LevelingTests]::Run()
