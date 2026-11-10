$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$source=Get-Content (Join-Path $kit 'Source/GroundLogisticsContents.cs') -Raw
$tests=Get-Content (Join-Path $kit 'Tools/GroundLogisticsTests.cs') -Raw
Add-Type -TypeDefinition ($source+"`n"+$tests)
$profiles=Get-Content (Join-Path $kit 'Reports/LOG_CAPACITIES.json') -Raw | ConvertFrom-Json
foreach($choice in $profiles.loadouts.PSObject.Properties){
 $resources=@($choice.Value)
 [GroundLogisticsTest]::AddChoice($choice.Name,[string[]]@($resources | ForEach-Object { $_.name }),[double[]]@($resources | ForEach-Object { $_.amount }),[double[]]@($resources | ForEach-Object { $_.maxAmount }))
}
[GroundLogisticsTest]::Run()
