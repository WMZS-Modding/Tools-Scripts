import json
import argparse
import sys
from pathlib import Path

def indent_json_file(input_path, output_path, indent_size=2):
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=indent_size, ensure_ascii=False)

        return True

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {input_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def find_json_files(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return []

    json_files = []
    for ext in ['*.json', '*.JSON']:
        json_files.extend(folder.glob(ext))

    return json_files

def create_output_folder(folder_path):
    output_folder = Path(folder_path)
    output_folder.mkdir(parents=True, exist_ok=True)

def process_folder(input_folder, output_folder, indent_size=2):
    create_output_folder(output_folder)

    json_files = find_json_files(input_folder)

    if not json_files:
        print(f"No JSON files found in '{input_folder}'")
        return (0, 0, 0)

    print(f"📁 Found {len(json_files)} JSON file(s) in '{input_folder}'")
    print("-" * 50)

    success_count = 0
    error_count = 0

    for input_file in json_files:
        output_file = Path(output_folder) / input_file.name

        print(f"Processing: {input_file.name}", end=" ")

        if indent_json_file(input_file, output_file, indent_size):
            print(f"Success -> {output_file}")
            success_count += 1
        else:
            print(f"Fail")
            error_count += 1

    return (success_count, error_count, len(json_files))

def main():
    parser = argparse.ArgumentParser(description='Indent multiple JSON files from a folder', formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', '--input', required=True, help='Input folder containing JSON files')
    parser.add_argument('-o', '--output', required=True, help='Output folder for indented JSON files')
    parser.add_argument('--indent', type=int, default=2, help='Number of spaces for indentation (default: 2)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    args = parser.parse_args()

    print("JSON File Indenter")
    print("=" * 50)
    print(f"Input folder:  {args.input}")
    print(f"Output folder: {args.output}")
    print(f"Indent size:   {args.indent} spaces")
    print("=" * 50)

    success, errors, total = process_folder(args.input, args.output, args.indent)

    print("=" * 50)
    print(f"Summary:")
    print(f" Total files:  {total}")
    print(f"   Successful: {success}")
    print(f"   Errors:     {errors}")

    if errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()