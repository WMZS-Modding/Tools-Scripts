# Delete-SiteHistory.ps1
A PowerShell script that can help you delete a site's web history without manually deleting it using Chrome and without deleting the whole thing using CCleaner.

This script:
- Works on Windows with Google Chrome profile
- Allows you to select 1 profile if you have multiple profiles
- Allows you to enter a link or keyword, it'll show the site's web history, then ask for confirmation
- Delete all related histories (`urls`, `visits`, `keyword_search_terms`) and runs `VACUUM` to shrink the History file size immediately
- Helps prevent the deletion of web history by an **unwanted** website like CCleaner

## Features
- Profile selection: Choose Chrome profile to clean the site's web history
- Delete site's web history: Delete only by link or keyword the user wrote
- Space recovery: Run with SQLite `VACUUM` to free up disk space
- Safe confirmation: Always asks before deleting
- No third-party tools required: Use `sqlite3.exe` only

## Requirements
- Windows 10 or later
- [SQLite command-line tools](https://www.sqlite.org/download.html) (`sqlite3.exe`) must be installed. How to install: Download the ZIP package named **`sqlite-tools-win64-x64-<version>.zip`** (or 32-bit if required), extract it, and make sure `sqlite3.exe` is accessible (either add to PATH or specify full path in the script).
- Google Chrome must be completely closed before running this script. You can use Task Manager to completely close
- Turn off sync. If not, Chrome will be still showing history

## How to use
1. Download or clone this repository (Use Green `Code` button)
2. Open PowerShell
3. Running the command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

4. Then running the script:

```powershell
{Path_to_script}\Delete-SiteHistory.ps1
```
5. Select Chrome profile by write a number (`0` is default)
6. Enter a URL or keyword (URL is recommended)
7. Confirm deletion with **Y** to proceed or **N** to cancel

##   Warnings
- Once the script has cleared a site's web history, it can't be undone. Make sure you really want to clear the web history before entering the command
- If Chrome is still open or closed without using Task Manager, the script will report an error saying it can't be executed
- This script only works with Chrome. If you want to use it with Edge or any browser, you have to modify the declaration inside the script

## Contribution
If you want to improve this script:
- Fork the repository and create a pull request
- Open an issue for bug reports or feature requests
