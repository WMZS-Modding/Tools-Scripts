import os
import sys
import argparse

WEIGHT_LOWERCASE = 0.5
WEIGHT_MIXED_CASE = 1.0
WEIGHT_UPPERCASE = 2.0

EMOJI_WEIGHTS = {
    # Normal scale (4-10)
    '🚫': 4,
    '💢': 5,
    '❌': 5,
    '😬': 6,
    '😠': 7,
    '😡': 8,
    '🤬': 9,
    '😈': 9.5,
    '👿': 10,

    # Exception scale (breaking the 10 limit)
    '🔥': 12,
    '⚡': 15,
    '💥': 20,
    '🌊': 30,
    '🌪': 40,
    '🌋': 50
}

# Crushing force for exception emojis (for metaphorical analysis)
EMOJI_CRUSHING_FORCE = {
    '🔥': '3 kgf',
    '⚡': '5 kgf',
    '💥': '20 kgf',
    '🌊': '1,000 tons',
    '🌪': '10 tons',
    '🌋': '2,000 tons',
}

SKIP_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx'
}

def get_emoji_weight(emoji: str) -> float:
    if emoji in EMOJI_CRUSHING_FORCE:
        force_str = EMOJI_CRUSHING_FORCE[emoji]
        if 'kgf' in force_str:
            return float(force_str.replace(' kgf', ''))
        elif 'tons' in force_str:
            return float(force_str.replace(' tons', '').replace(',', '')) * 1000
    return 0.0

def count_emoji_points(text: str) -> tuple:
    total_points = 0
    total_emoji_weights = 0.0
    emoji_counts = {}

    for emoji, weight in EMOJI_WEIGHTS.items():
        count = text.count(emoji)
        if count > 0:
            emoji_counts[emoji] = count
            total_points += count * weight
            total_emoji_weights += count * get_emoji_weight(emoji)

    return total_points, total_emoji_weights, emoji_counts

def calculate_crushing_force(total_points: float, emoji_counts: dict) -> float:
    total_emoji_weights = 0.0

    for emoji, count in emoji_counts.items():
        total_emoji_weights += count * get_emoji_weight(emoji)

    return total_points + total_emoji_weights

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

    emoji_points = 0
    emoji_weights = 0.0
    emoji_counts = {}
    if emoji_mode:
        emoji_points, emoji_weights, emoji_counts = count_emoji_points(text)

    total_points = points_from_case + emoji_points

    crushing_force = calculate_crushing_force(total_points, emoji_counts) if emoji_mode else total_points

    return {
        'total_chars': total_chars,
        'uppercase_chars': uppercase_chars,
        'mixed_chars': mixed_chars,
        'lowercase_chars': lowercase_chars,
        'points_from_case': points_from_case,
        'emoji_points': emoji_points,
        'emoji_weights': emoji_weights,
        'emoji_counts': emoji_counts,
        'total_points': total_points,
        'crushing_force': crushing_force,
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
    total_emoji_weights = 0.0
    overall_emoji_counts = {}
    file_count = 0

    for root, files in os.walk(folderpath):
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
                total_emoji_weights += result.get('emoji_weights', 0)

                for emoji, count in result.get('emoji_counts', {}).items():
                    overall_emoji_counts[emoji] = overall_emoji_counts.get(emoji, 0) + count

                file_count += 1
                if verbose:
                    force = result.get('crushing_force', result['total_points'])
                    print(f"Processed: {filepath} → {result['total_points']:.2f} points (emoji: {result['emoji_points']:.2f}, force: {force:.2f})")

    total_crushing_force = calculate_crushing_force(total_points, overall_emoji_counts) if emoji_mode else total_points

    return {
        'total_points': total_points,
        'total_case_points': total_case_points,
        'total_emoji_points': total_emoji_points,
        'total_emoji_weights': total_emoji_weights,
        'total_crushing_force': total_crushing_force,
        'overall_emoji_counts': overall_emoji_counts,
        'file_count': file_count,
        'files': folder_results,
        'emoji_mode': emoji_mode
    }

def print_emoji_breakdown(emoji_counts: dict, indent: str = "    "):
    if not emoji_counts:
        print(f"{indent}No emojis found.")
        return

    sorted_emojis = sorted(emoji_counts.items(), key=lambda x: EMOJI_WEIGHTS.get(x[0], 0), reverse=True)

    for emoji, count in sorted_emojis:
        if count > 0:
            weight = EMOJI_WEIGHTS.get(emoji, 0)
            points = count * weight
            force = EMOJI_CRUSHING_FORCE.get(emoji, None)

            if force:
                print(f"{indent}{emoji} × {count} = {points:.2f} points  [{force}]")
            else:
                print(f"{indent}{emoji} × {count} = {points:.2f} points")

def format_force(force: float, no_abbreviation: bool = False) -> str:
    if no_abbreviation:
        return f"{force:.2f} kgf"

    if force >= 1000000:
        return f"{force/1000000:.2f} million kgf"
    elif force >= 1000:
        return f"{force/1000:.2f} tons"
    else:
        return f"{force:.2f} kgf"

def print_single_result(result: dict, filename: str, emoji_mode: bool, no_abbreviation: bool = False):
    if not result:
        return

    print("=" * 60)
    print(f"ANALYSIS: {filename}")
    print("=" * 60)
    print(f"Total Anger Points: {result['total_points']:.2f}")

    if emoji_mode:
        print(f"  - From case: {result['points_from_case']:.2f}")
        print(f"  - From emojis: {result['emoji_points']:.2f}")
        print(f"  Total Crushing Force: {format_force(result.get('crushing_force', result['total_points']), no_abbreviation)}")

        emoji_counts = result.get('emoji_counts', {})
        if emoji_counts:
            print("  Emoji Breakdown:")
            print_emoji_breakdown(emoji_counts)

    print(f"Total Lines: {result['total_lines']}")
    print(f"Total Characters: {result['total_chars']}")
    print(f"Uppercase Characters: {result['uppercase_chars']}")
    print(f"Mixed Case Characters: {result['mixed_chars']}")
    print(f"Lowercase Characters: {result['lowercase_chars']}")
    print("=" * 60)
    print()

def print_folder_result(result: dict, folderpath: str, no_abbreviation: bool = False):
    print("=" * 60)
    print(f"FOLDER ANALYSIS: {folderpath}")
    print("=" * 60)
    print(f"Total Anger Points: {result['total_points']:.2f}")

    if result['emoji_mode']:
        print(f"  - From case: {result['total_case_points']:.2f}")
        print(f"  - From emojis: {result['total_emoji_points']:.2f}")
        print(f"  Total Crushing Force: {format_force(result.get('total_crushing_force', result['total_points']), no_abbreviation)}")

        overall_emoji_counts = result.get('overall_emoji_counts', {})
        if overall_emoji_counts:
            print("  Overall Emoji Breakdown:")
            print_emoji_breakdown(overall_emoji_counts)

    print(f"Files Processed: {result['file_count']}")
    print("-" * 40)

    sorted_files = sorted(result['files'].items(), key=lambda x: x[1]['total_points'], reverse=True)

    for filepath, file_result in sorted_files:
        if result['emoji_mode']:
            force = file_result.get('crushing_force', file_result['total_points'])
            print(f"  {os.path.basename(filepath)}: {file_result['total_points']:.2f} points (force: {format_force(force, no_abbreviation)})")
        else:
            print(f"  {os.path.basename(filepath)}: {file_result['total_points']:.2f} points")

    print("=" * 60)
    print()

def main():
    parser = argparse.ArgumentParser(description="Count anger points based on character case and emoji analysis.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--input', help='Path to a single editable text file')
    group.add_argument('-f', '--folder', help='Path to a folder containing text files')
    parser.add_argument('--emoji', action='store_true', default=False, help='Enable emoji anger scoring (default: False)')
    parser.add_argument('--no-abbreviation', action='store_true', default=False, help='Show full unit names instead of abbreviations (default: False)')
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
        print_single_result(result, args.input, args.emoji, args.no_abbreviation)
    elif args.folder:
        if not os.path.isdir(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            sys.exit(1)

        result = process_folder(args.folder, args.emoji, args.verbose)
        print_folder_result(result, args.folder, args.no_abbreviation)

if __name__ == "__main__":
    main()