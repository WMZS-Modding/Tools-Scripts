import os
import difflib
import argparse

SKIP_EXTS = {'.png','.jpg','.jpeg','.gif','.mp3','.wav','.ogg','.mp4','.avi','.webm','.flac','.bmp','.tga','.ico'}

def should_skip(file_path: str) -> bool:
    _, ext = os.path.splitext(file_path.lower())
    return ext in SKIP_EXTS

def find_by_name(root, filename):
    matches = []
    for dirpath, _, files in os.walk(root):
        if filename in files:
            matches.append(os.path.join(dirpath, filename))
    return matches

def compare_files(original_file, modified_file):
    with open(modified_file, 'r', errors='ignore') as f:
        mod_lines = f.readlines()
    if os.path.exists(original_file):
        with open(original_file, 'r', errors='ignore') as f:
            orig_lines = f.readlines()
        diff = difflib.unified_diff(orig_lines, mod_lines,
                                    fromfile=original_file,
                                    tofile=modified_file,
                                    lineterm='')
        return '\n'.join(diff)
    else:
        return '\n'.join('+ ' + line.rstrip('\n') for line in mod_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', help='Original folder')
    parser.add_argument('-mo', '--modified_folder', required=True, help='Modified folder')
    parser.add_argument('-o', '--output_folder', required=True, help='Output folder')
    args = parser.parse_args()

    original_root = os.path.abspath(args.input_folder)
    modified_root = os.path.abspath(args.modified_folder)
    output_root = os.path.abspath(args.output_folder)

    for dirpath, _, filenames in os.walk(modified_root):
        for fname in filenames:
            mod_file = os.path.join(dirpath, fname)
            if should_skip(mod_file):
                continue

            rel_path = os.path.relpath(mod_file, modified_root)
            orig_file = os.path.join(original_root, rel_path)

            if not os.path.exists(orig_file):
                matches = find_by_name(original_root, fname)
                if len(matches) == 1:
                    orig_file = matches[0]

            diff_text = compare_files(orig_file, mod_file)
            if not diff_text.strip():
                continue

            out_path = os.path.join(output_root, rel_path) + '.cfc'
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(diff_text)

if __name__ == '__main__':
    main()
