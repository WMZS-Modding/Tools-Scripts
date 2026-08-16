import os
import sys
import argparse

WEIGHT_LOWERCASE = 0.5
WEIGHT_MIXED_CASE = 1.0
WEIGHT_UPPERCASE = 2.0

EMOJI_WEIGHTS = {
    '🚫': 4,
    '💢': 5,
    '❌': 5,
    '😬': 6,
    '😠': 7,
    '😡': 8,
    '🤬': 9,
}

SKIP_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx'
}

def count_emoji_points(text: str) -> int:
    total = 0
    for emoji, weight in EMOJI_WEIGHTS.items():
        count = text.count(emoji)
        total += count * weight
    return total

def analyze_text(text: str, emoji_mode: bool = False) -> dict:
    total_chars = len(text)

    uppercase_chars = 0
    lowercase_chars = 0
    mixed_chars = 0

    for c in text:
        if c.isalpha():
            if c.isupper():
                uppercase_chars += 1
            elif c.islower():
                lowercase_chars += 1
            else:
                mixed_chars += 1

    points_from_case = ((uppercase_chars * WEIGHT_UPPERCASE) + (mixed_chars * WEIGHT_MIXED_CASE) + (lowercase_chars * WEIGHT_LOWERCASE))

    emoji_points = count_emoji_points(text) if emoji_mode else 0

    total_points = points_from_case + emoji_points

    return {
        'total_chars': total_chars,
        'uppercase_chars': uppercase_chars,
        'mixed_chars': mixed_chars,
        'lowercase_chars': lowercase_chars,
        'points_from_case': points_from_case,
        'emoji_points': emoji_points,
        'total_points': total_points,
        'has_emoji': emoji_points > 0,
        'emoji_mode': emoji_mode
    }

def process_text(content: str, emoji_mode: bool = False) -> dict:
    result = analyze_text(content, emoji_mode)
    result['total_lines'] = len(content.splitlines())
    result['emoji_mode'] = emoji_mode
    return result

def process_file(filepath: str, emoji_mode: bool = False, verbose: bool = False) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    result = process_text(content, emoji_mode)
    result['filename'] = filepath
    return result

def is_binary_file(filepath: str) -> bool:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
    except:
        return True

    return False

def process_folder(folderpath: str, emoji_mode: bool = False, verbose: bool = False) -> dict:
    folder_results = {}
    total_points = 0
    total_case_points = 0
    total_emoji_points = 0
    file_count = 0

    for root, dirs, files in os.walk(folderpath):
        for filename in files:
            filepath = os.path.join(root, filename)

            if is_binary_file(filepath):
                if verbose:
                    print(f"Skipping binary file: {filepath}")
                continue

            result = process_file(filepath, emoji_mode, verbose)
            if result:
                folder_results[filepath] = result
                total_points += result['total_points']
                total_case_points += result['points_from_case']
                total_emoji_points += result['emoji_points']
                file_count += 1
                if verbose:
                    print(f"Processed: {filepath} → {result['total_points']} points (emoji: {result['emoji_points']})")

    return {
        'total_points': total_points,
        'total_case_points': total_case_points,
        'total_emoji_points': total_emoji_points,
        'file_count': file_count,
        'files': folder_results,
        'emoji_mode': emoji_mode
    }

def print_single_result(result: dict, filename: str, emoji_mode: bool):
    if not result:
        return

    print("=" * 60)
    print(f"ANALYSIS: {filename}")
    print("=" * 60)
    print(f"Total Anger Points: {result['total_points']:.2f}")
    if emoji_mode:
        print(f"  - From case: {result['points_from_case']:.2f}")
        print(f"  - From emojis: {result['emoji_points']}")
    print(f"Total Lines: {result['total_lines']}")
    print(f"Total Characters: {result['total_chars']}")
    print(f"Uppercase Characters: {result['uppercase_chars']}")
    print(f"Mixed Case Characters: {result['mixed_chars']}")
    print(f"Lowercase Characters: {result['lowercase_chars']}")
    print("=" * 60)
    print()

def print_folder_result(result: dict, folderpath: str):
    print("=" * 60)
    print(f"FOLDER ANALYSIS: {folderpath}")
    print("=" * 60)
    print(f"Total Anger Points: {result['total_points']:.2f}")
    if result['emoji_mode']:
        print(f"  - From case: {result['total_case_points']:.2f}")
        print(f"  - From emojis: {result['total_emoji_points']}")
    print(f"Files Processed: {result['file_count']}")
    print("-" * 40)

    sorted_files = sorted(result['files'].items(), key=lambda x: x[1]['total_points'], reverse=True)

    for filepath, file_result in sorted_files:
        if result['emoji_mode']:
            print(f"  {os.path.basename(filepath)}: {file_result['total_points']:.2f} points (emoji: {file_result['emoji_points']})")
        else:
            print(f"  {os.path.basename(filepath)}: {file_result['total_points']:.2f} points")

    print("=" * 60)
    print()

def main():
    parser = argparse.ArgumentParser(description="Count anger points based on character case analysis.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--input', help='Path to a single editable text file')
    group.add_argument('-f', '--folder', help='Path to a folder containing text files')
    parser.add_argument('--emoji', action='store_true', default=False, help='Enable emoji anger scoring (default: False)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')

    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: File not found: {args.input}")
            sys.exit(1)

        if is_binary_file(args.input):
            print(f"Error: File appears to be binary: {args.input}")
            sys.exit(1)

        result = process_file(args.input, args.emoji, args.verbose)
        print_single_result(result, args.input, args.emoji)
    elif args.folder:
        if not os.path.isdir(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            sys.exit(1)

        result = process_folder(args.folder, args.emoji, args.verbose)
        print_folder_result(result, args.folder)

if __name__ == "__main__":
    main()