# Delete SiteHistory
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

## Warnings
- Once the script has cleared a site's web history, it can't be undone. Make sure you really want to clear the web history before entering the command
- If Chrome is still open or closed without using Task Manager, the script will report an error saying it can't be executed
- This script only works with Chrome. If you want to use it with Edge or any browser, you have to modify the declaration inside the script

# Conversations Decode Extractor (V1)
Python tool to decode and extract conversations from ChatGPT and DeepSeek exported files. Supports 4 versions:
- `ConversationsDecodeExtractor.py`: Combines all ChatGPT's conversations into a single TXT file
- `ConversationsDecodeExtractor2.py`: Splits ChatGPT's onversations into separate TXT files
- `ConversationsDecodeExtractor3.py`: Combines all DeepSeek's conversations into a single TXT file
- `ConversationsDecodeExtractor4.py`: Splits DeepSeek's conversations into separate TXT files

## Requirements
- Python: any version that supports it
- JSON files from ChatGPT and DeepSeek (`conversations.json` is the required file, included in the ZIP file, which was exported from the `Export Data` button)

## Usage
### ConversationsDecodeExtractor.py
Run the script with the command:
```bash
python ConversationsDecodeExtractor.py "input_json.json" -o "output_txt.txt"
```

Result: a file `output_txt.txt` (or whatever name you give it) is exported containing the entire ChatGPT's conversation

### ConversationsDecodeExtractor2.py
Run the script with the command:
```bash
python ConversationsDecodeExtractor2.py "input_json.json" -o "output_folder"
```

Result: A bunch of TXT files containing ChatGPT's conversations appear in the folder.

The TXT files' names are in the form: `[number]_[name].txt`

### ConversationsDecodeExtractor3.py
Run the script with the command:
```bash
python ConversationsDecodeExtractor3.py "input_json.json" -o "output_txt.txt"
```

Result: a file `output_txt.txt` (or whatever name you give it) is exported containing the entire DeepSeek's conversation

### ConversationsDecodeExtractor4.py
Run the script with the command:
```bash
python ConversationsDecodeExtractor4.py "input_json.json" -o "output_folder"
```

Result: A bunch of TXT files containing DeepSeek's conversations appear in the folder.

The TXT files' names are in the form: `[number]_[name].txt`

## Notes
### ChatGPT
- The scripts only extracts `content_type="text"` and `"role"`, i.e. messages, roles and replies
- Other content like `user_editable_context` will be ignored
- If the conversation is too long, I recommend using `ConversationsDecodeExtractor2.py` so you can find it easier without having to open a huge file and experiencing lag
### DeepSeek
- The scripts only extract user's and assistant's replies + role
- If the conversation is too long, I recommend using `ConversationsDecodeExtractor4.py` so you can find it easier without having to open a huge file and experiencing lag

# CompareFolder
A python tool can show changes with "−" and "+"

## Features
- Export results from Modified Folder with extension: `.cfc`
- Add `−` and `+` to show changes

## Requirements
- 2 folders:
  + Original folder
  + Modified folder
- Extension: [comparing-changes](https://marketplace.visualstudio.com/items?itemName=SuperHero2010.comparing-changes)

## How to use
1. Download [CompareFolder.py](https://github.com/WMZS-Modding/Tools-Scripts/blob/main/src/CompareFolder.py) and [comparing-changes](https://marketplace.visualstudio.com/items?itemName=SuperHero2010.comparing-changes) extension
2. Run command on Command Prompt:
```bash
python CompareFolder.py "{input_folder}" -mo "{modified_folder}" -o "{output_folder_result}"
```

3. Go to `output_folder_result` and click any files with `.cfc` extension
4. You can see `−` and `+` are coloring red and green

## Note
- Python will skip media files, unreadable files
- If you run script and show `Python wasn't found`, you can run this command instead:
```bash
py CompareFolder.py "{input_folder}" -mo "{modified_folder}" -o "{output_folder_result}"
```

# Conversations Extractor (V2)

Second versions of the old scripts. They have similar functionality, but have been significantly improved. 2 versions are supported:
- `ConversationsExtractor.py`: Exports DeepSeek's `conversations.json` to multiple TXT files
- `ConversationsExtractor2.py`: Another variant, exports ChatGPT's `conversations.json` to multiple TXT files

## Requirements
- Python: any version that supports it
- JSON files from ChatGPT and DeepSeek (`conversations.json` is the required file, included in the ZIP file, which was exported from the `Export Data` button)

## Usage
### ConversationsExtractor.py
```bash
python ConversationsExtractor.py "input_json.json" -o "output_folder_result"
```

Result: A bunch of TXT files containing DeepSeek's conversations appear in the folder. Same as V1 scripts, but it has many changes

### ConversationsExtractor2.py
```bash
python ConversationsExtractor2.py "input_json.json" -o "output_folder_result"
```

Result: A bunch of TXT files containing ChatGPT's conversations appear in the folder. Same as V1 scripts, but it has many changes

## Changes in V2
- New message counter: Now you can know how many main messages and how many full messages in the conversation
- Ignore system messages and empty messages
- Context counter: This is the biggest update. Now you can know how many main contexts and how many full contexts

## Notes
These scripts are calculate characters of your chat histories. To know your real context counts, use this mathematical formulas: `Context ÷ 4`

# Glitch effect shader web generator
This is a website that helps you apply Glitch shaders to your images.

## Features
- Glitch HTML: Main HTML web script to generate frame
- `ClearBlackBackground.py`: It helps you clear the black background if you don't want
- `AnimationFolder2GIF.py`: It helps you merge your animation folder to GIF image

## Requirements
You need install `Pillow`:

```bash
pip install pillow
```

or:

```bash
python -m pip install pillow
```

## Usage
- First, go to `Glitch.html` by right clicking it and clicking `Open with/Google Chrome` or any browser
- Then, choose your image. I recommend choosing PNG image. Change amount of Glitch Speed and Glitch Amount as you want
- Next, click `Export ZIP (60 Frames)`. Extract ZIP to a folder
- Finally, use these Python scripts:

```bash
python ClearBlackBackground.py "input_folder" -o "output_folder" -t threshold
```

```bash
python AnimationFolder2GIF.py "input_folder_result" -o "Glitch.gif"
```

## Note
- Web will generate all frames that were colored background with black
- `ClearBlackBackground.py` might remove too much/little. Adjust `threshold` (0-255, default: 30)
- If you don't want the 10s and 30 FPS limits, you can change this:

```javascript
const totalFrames = 60;
const fps = 30;
```

If you don't know how to set duration of the frames, use this formula: `Frames = Duration × FPS`
- `Frames`: `totalFrames`
- `Duration`: How many seconds you want for your animation
- `FPS`: `fps`

# Gradient Color Generator
A simple script that generates many color codes from color input to color output

## Usage
1. Run this script:

```bash
python Gradient.py
```

2. Answer these question:
- Color input (hex format)
- Color output (hex format)
- "How many color codes do you want to your gradient color?" (Maximum: 32)

## Note
If you dislike `32` limit, change this code:

```python
if 2 <= num_colors <= 32:
```

But please keep `2` value, the script will be error if you change this value

# Glow Gradient Frame Generator for custom FNF note skins
2 simple python scripts can help you create frames of your note skins

## Usage
1. First, you must have 4 note frames (not glow, not gray)
2. Run script:

```bash
python GlowGradientFrame.py -i "input_frame.png" -o "output_folder" -f "frame_number" --size "frame_size" --max-radius "radius_number"
```

3. Go to the output folder and run script:

```bash
python replace_black_edges.py "input_folder"
```

4. Do the same to other note frames
5. Put them to a separate folder
6. Go to [FNF-Spritesheet-XML-generator-web](https://uncertainprod.github.io/FNF-Spritesheet-XML-generator-Web/), select all your frames on that folder and export

# Contribution
If you want to improve this script:
- Fork the repository and create a pull request
- Open an issue for bug reports or feature requests