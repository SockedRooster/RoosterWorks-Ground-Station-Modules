param([string]$KspRoot='D:/SteamLibrary/steamapps/common/Kerbal Space Program')
$ErrorActionPreference='Stop'
$kit=Split-Path -Parent $PSScriptRoot
$managed=Join-Path $KspRoot 'KSP_x64_Data/Managed'
$argsList=@('C:/Program Files/dotnet/sdk/10.0.401/Roslyn/bincore/csc.dll','/nologo','/target:library','/nostdlib+','/optimize+','/deterministic+','/langversion:7.3')
foreach($reference in @('mscorlib.dll','System.dll','System.Core.dll','Assembly-CSharp.dll','UnityEngine.dll','UnityEngine.CoreModule.dll','UnityEngine.PhysicsModule.dll')) { $argsList += '/reference:'+(Join-Path $managed $reference) }
$argsList += '/out:'+(Join-Path $kit 'GameData/RoosterWorksGroundModules/Plugins/RoosterWorksGroundDeploy.dll')
$argsList += Join-Path $kit 'Source/GroundDeploy.cs'
$argsList += Join-Path $kit 'Source/GroundFit.cs'
$argsList += Join-Path $kit 'Source/GroundLevel.cs'
$argsList += Join-Path $kit 'Source/GroundTether.cs'
$argsList += Join-Path $kit 'Source/GroundDocking.cs'
$argsList += Join-Path $kit 'Source/EndWindowLink.cs'
$argsList += Join-Path $kit 'Source/CollapsibleTube.cs'
$argsList += Join-Path $kit 'Source/ExteriorLight.cs'
$argsList += Join-Path $kit 'Source/PodRelease.cs'
$argsList += Join-Path $kit 'Source/GroundLogisticsContents.cs'
& dotnet @argsList
if($LASTEXITCODE -ne 0){throw 'Ground deployment runtime compilation failed'}
Write-Output 'PASS compiled deployment controller against installed KSP 1.12.5 assemblies'
