import os
import argparse
import sys
from pathlib import Path
from typing import Set

BINARY_EXTENSIONS: Set[str] = {
    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma',
    # Video
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp', '.heic',
    # System
    '.exe', '.dll', '.so', '.dylib', '.sys', '.bin', '.dat',
    # Archives
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
    # Documents (binary formats)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Other binaries
    '.pyc', '.pyo', '.class', '.o', '.obj', '.lib'
}

def is_text_file(file_path: Path) -> bool:
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return False

    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return False
        return True
    except:
        return False

def clean_fake_empty_lines(content: str) -> str:
    lines = content.splitlines(True)
    cleaned_lines = []
    previous_was_empty = False

    for line in lines:
        if line.strip() == '':
            if not previous_was_empty:
                cleaned_lines.append('\n')
                previous_was_empty = True
        else:
            cleaned_lines.append(line)
            previous_was_empty = False

    return ''.join(cleaned_lines)

def clean_file(input_path: Path, output_path: Path) -> tuple:
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
            original_content = infile.read()

        cleaned_content = clean_fake_empty_lines(original_content)

        original_lines = original_content.splitlines()
        cleaned_lines = cleaned_content.splitlines()
        original_empty_count = sum(1 for line in original_lines if line.strip() == '')
        cleaned_empty_count = sum(1 for line in cleaned_lines if line.strip() == '')

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_content)

        lines_removed = len(original_lines) - len(cleaned_lines)
        empty_lines_collapsed = original_empty_count - cleaned_empty_count

        return (True, lines_removed, empty_lines_collapsed)

    except Exception as e:
        return (False, 0, str(e))

def process_folder(input_folder: Path, output_folder: Path, preserve_structure: bool = True) -> dict:
    stats = {
        'total_files': 0,
        'text_files': 0,
        'binary_files': 0,
        'processed': 0,
        'errors': 0,
        'total_lines_removed': 0,
        'total_empty_collapsed': 0,
        'failed_files': []
    }

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            input_file = Path(root) / file
            stats['total_files'] += 1

            if preserve_structure:
                relative_path = input_file.relative_to(input_folder)
                output_file = output_folder / relative_path
            else:
                output_file = output_folder / file

            if not is_text_file(input_file):
                stats['binary_files'] += 1
                print(f"Skipping binary file: {input_file}")
                continue

            stats['text_files'] += 1

            success, lines_removed, empty_collapsed = clean_file(input_file, output_file)

            if success:
                stats['processed'] += 1
                stats['total_lines_removed'] += lines_removed
                stats['total_empty_collapsed'] += empty_collapsed

                if lines_removed > 0 or empty_collapsed > 0:
                    print(f"{relative_path if preserve_structure else input_file.name}")
                    if lines_removed > 0:
                        print(f"   └─ Removed {lines_removed} line(s)")
                    if empty_collapsed > 0:
                        print(f"   └─ Collapsed {empty_collapsed} empty line(s)")
            else:
                stats['errors'] += 1
                stats['failed_files'].append(str(input_file))
                print(f"Error processing {input_file}: {empty_collapsed}")

                try:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(input_file, output_file)
                    print(f"   └─ Copied without changes")
                except:
                    pass

    return stats

def main():
    parser = argparse.ArgumentParser(description='Remove fake empty lines from text files and collapse multiple empty lines', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--input', required=True, help='Input folder containing files to process')
    parser.add_argument('-o', '--output', required=True, help='Output folder for cleaned files')
    parser.add_argument('--no-preserve', action='store_true', help='Do not preserve folder structure (put all files in output folder)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')

    args = parser.parse_args()

    input_folder = Path(args.input)
    output_folder = Path(args.output)

    if not input_folder.exists():
        print(f"Input folder not found: {input_folder}")
        sys.exit(1)

    print("Text File Cleaner - Remove Fake Empty Lines & Collapse Multiple Empty Lines")
    print("=" * 70)
    print(f"Input folder:  {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Preserve structure: {'No' if args.no_preserve else 'Yes'}")
    print("=" * 70)

    stats = process_folder(input_folder, output_folder, not args.no_preserve)

    print("\n" + "=" * 70)
    print("Summary:")
    print(f"   Total files scanned:     {stats['total_files']}")
    print(f"   Text files found:      {stats['text_files']}")
    print(f"   Binary files skipped:  {stats['binary_files']}")
    print(f"   Successfully cleaned:  {stats['processed']}")
    print(f"   Errors:                {stats['errors']}")
    print(f"   Total lines removed:   {stats['total_lines_removed']}")
    print(f"   Empty lines collapsed: {stats['total_empty_collapsed']}")

    if stats['failed_files']:
        print(f"\nFailed files ({len(stats['failed_files'])}):")
        for failed in stats['failed_files'][:10]:  # Show first 10
            print(f"   - {failed}")
        if len(stats['failed_files']) > 10:
            print(f"   ... and {len(stats['failed_files']) - 10} more")

    if stats['errors'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()