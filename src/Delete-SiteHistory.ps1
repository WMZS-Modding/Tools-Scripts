# --- Configuration ---
# List all profiles with History folder
$basePath = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$profiles = Get-ChildItem $basePath -Directory | Where-Object {
    Test-Path "$($_.FullName)\History"
}

if ($profiles.Count -eq 0) {
    Write-Host "No Chrome profiles with history found."
    exit
}

Write-Host "Select the Chrome profile you want to clear history from:"
for ($i = 0; $i -lt $profiles.Count; $i++) {
    Write-Host "[$i] $($profiles[$i].Name)"
}

$index = Read-Host "Enter profile number"
if ($index -notmatch '^\d+$' -or $index -ge $profiles.Count) {
    Write-Host "Invalid selection."
    exit
}

$profilePath = $profiles[$index].FullName
$historyPath = "$profilePath\History"

if (!(Test-Path $historyPath)) {
    Write-Host "Chrome history file not found. Check the path."
    exit
}

$link = Read-Host "Enter the link (or keyword) to delete"

$tempPath = "$env:TEMP\History_copy"
Copy-Item $historyPath $tempPath -Force

# Identify sqlite3.exe
$sqlitePath = (Get-Command sqlite3.exe -ErrorAction SilentlyContinue).Source
if (-not $sqlitePath) {
    $possible = "C:\Program Files\SQLite\sqlite3.exe"
    if (Test-Path $possible) { $sqlitePath = $possible }
    else {
        Write-Host "sqlite3.exe not found. Download the ZIP package (sqlite-tools) and put it in PATH."
        exit
    }
}

# Count histories before deleting
$queryCount = "SELECT COUNT(*) FROM urls WHERE url LIKE '%$link%';"
$count = & $sqlitePath $tempPath $queryCount
Write-Host "There are $count history items containing '$link'"

if ($count -eq 0) {
    Write-Host "There is nothing to delete."
    Remove-Item $tempPath
    exit
}

$confirm = Read-Host "Do you want to delete these histories? (Y/N)"
if ($confirm -match '^[Yy]$') {
    $deleteSQL = @"
DELETE FROM visits WHERE url IN (SELECT id FROM urls WHERE url LIKE '%$link%');
DELETE FROM keyword_search_terms WHERE url_id IN (SELECT id FROM urls WHERE url LIKE '%$link%');
DELETE FROM urls WHERE url LIKE '%$link%';
VACUUM;
"@
    & $sqlitePath $historyPath $deleteSQL
    Write-Host "Deleted $count items and collapsed History file."
} else {
    Write-Host "Operation cancelled."
}

Remove-Item $tempPath
