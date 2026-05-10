import argparse
import sys
from pathlib import Path

def has_only_whitespace(line):
    return line.strip() == '' and len(line) > 0 and line != '\n'

def clean_fake_empty_lines(content):
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

def clean_fake_empty_lines_advanced(content):
    lines = content.splitlines(True)
    cleaned_lines = []

    for line in lines:
        if line.strip() == '':
            continue

        cleaned_lines.append(line.rstrip() + '\n')

    return ''.join(cleaned_lines)

def clean_python_file(input_path, output_path, advanced=False):
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()

        if advanced:
            cleaned_content = clean_fake_empty_lines_advanced(content)
        else:
            cleaned_content = clean_fake_empty_lines(content)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_content)

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def find_python_files(folder_path, recursive=False):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return []

    if recursive:
        python_files = list(folder.rglob('*.py'))
    else:
        python_files = list(folder.glob('*.py'))

    return python_files

def create_output_folder(folder_path):
    output_folder = Path(folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

def process_folder(input_folder, output_folder, recursive=False, advanced=False, preserve_structure=False):
    python_files = find_python_files(input_folder, recursive)

    if not python_files:
        print(f"No Python files found in '{input_folder}'")
        return (0, 0, 0)

    print(f"Found {len(python_files)} Python file(s) in '{input_folder}'")
    print("-" * 60)

    success_count = 0
    error_count = 0

    for input_file in python_files:
        if preserve_structure:
            relative_path = input_file.relative_to(input_folder)
            output_file = Path(output_folder) / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_file = Path(output_folder) / input_file.name

        print(f"Processing: {input_file}", end=" ")

        if clean_python_file(input_file, output_file, advanced):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    original_lines = f.readlines()
                with open(output_file, 'r', encoding='utf-8') as f:
                    cleaned_lines = f.readlines()

                removed = len(original_lines) - len(cleaned_lines)
                print(f"Done! -> {output_file} (removed {removed} fake empty line(s))")
            except:
                print(f"Done! -> {output_file}")
            success_count += 1
        else:
            print(f"Failed to process {input_file}")
            error_count += 1

    return (success_count, error_count, len(python_files))

def main():
    parser = argparse.ArgumentParser(description='Remove fake empty lines (lines with only spaces/tabs) from Python files', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--input', required=True, help='Input folder containing Python files')
    parser.add_argument('-o', '--output', required=True, help='Output folder for cleaned Python files')
    parser.add_argument('-r', '--recursive', action='store_true', help='Process subdirectories recursively')
    parser.add_argument('-a', '--advanced', action='store_true', help='Also remove trailing whitespace from lines')
    parser.add_argument('--preserve', action='store_true', help='Preserve folder structure in output')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    args = parser.parse_args()

    print("Python Fake Empty Lines Remover")
    print("=" * 60)
    print(f"Input folder:  {args.input}")
    print(f"Output folder: {args.output}")
    print(f"Mode:          {'Advanced' if args.advanced else 'Standard'}")
    print(f"Recursive:     {'Yes' if args.recursive else 'No'}")
    print(f"Preserve structure: {'Yes' if args.preserve else 'No'}")
    print("=" * 60)

    success, errors, total = process_folder(args.input, args.output, args.recursive, args.advanced, args.preserve)

    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Total files:  {total}")
    print(f"   Successful: {success}")
    print(f"   Errors:     {errors}")

    if errors > 0:
        sys.exit(1)
    elif success > 0:
        print(f"\nSuccessfully cleaned {success} Python file(s)!")

if __name__ == "__main__":
    main()