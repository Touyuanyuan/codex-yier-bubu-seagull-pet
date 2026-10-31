#requires -Version 5.1
[CmdletBinding()]
param([string] $CodexHome)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$petId = 'yier-bubu-handholding-seagull'
$sourceDir = Join-Path $PSScriptRoot 'pet'
if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
}
$petDir = Join-Path (Join-Path $CodexHome 'pets') $petId
foreach ($name in @('pet.json','spritesheet.webp')) {
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDir $name) -PathType Leaf)) {
        throw ('Missing pet/' + $name + '. Extract the complete package first.')
    }
}
$manifest = Get-Content -LiteralPath (Join-Path $sourceDir 'pet.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.id -ne $petId -or $manifest.spriteVersionNumber -ne 2 -or $manifest.spritesheetPath -ne 'spritesheet.webp') {
    throw 'The pet manifest does not match this installer.'
}
if (Test-Path -LiteralPath $petDir) {
    $targetItem = Get-Item -LiteralPath $petDir -Force
    if (-not $targetItem.PSIsContainer -or ($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Destination must be an ordinary directory.' }
    foreach ($name in @('pet.json','spritesheet.webp')) {
        $existing = Join-Path $petDir $name
        if ((Test-Path -LiteralPath $existing) -and ((Get-Item -LiteralPath $existing -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Destination files must not be links.' }
    }
    $backupDir = Join-Path (Join-Path $CodexHome 'pet-backups') ($petId + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    foreach ($name in @('pet.json','spritesheet.webp')) {
        $old = Join-Path $petDir $name
        if (Test-Path -LiteralPath $old -PathType Leaf) { Copy-Item -LiteralPath $old -Destination (Join-Path $backupDir $name) }
    }
    Write-Host ('Previous pet files backed up to: ' + $backupDir)
}
New-Item -ItemType Directory -Path $petDir -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $sourceDir 'pet.json') -Destination (Join-Path $petDir 'pet.json') -Force
Copy-Item -LiteralPath (Join-Path $sourceDir 'spritesheet.webp') -Destination (Join-Path $petDir 'spritesheet.webp') -Force
Write-Host ('Installed: ' + $manifest.displayName)
Write-Host ('Pet folder: ' + $petDir)
Write-Host 'In Codex, refresh the pet list under Settings > Mini and pets, then select this pet.'
