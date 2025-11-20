import os
import sys
import argparse
from PIL import Image
import glob

def remove_black_background(input_path, output_path, threshold=30):
    try:
        with Image.open(input_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            data = img.getdata()

            new_data = []
            for item in data:
                brightness = (item[0] + item[1] + item[2]) / 3

                if brightness < threshold:
                    new_data.append((0, 0, 0, 0))
                else:
                    new_data.append(item)

            img.putdata(new_data)
            img.save(output_path, 'PNG')
            return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def process_folder(input_folder, output_folder, threshold=30):
    os.makedirs(output_folder, exist_ok=True)

    extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']

    processed_count = 0
    total_count = 0

    for ext in extensions:
        for input_path in glob.glob(os.path.join(input_folder, ext)):
            total_count += 1
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.png')

            print(f"Processing: {filename}")
            if remove_black_background(input_path, output_path, threshold):
                processed_count += 1

    print(f"\nSuccessfully processed {processed_count}/{total_count} images")
    print(f"Output folder: {output_folder}")

def main():
    parser = argparse.ArgumentParser(description='Remove black background from images and make transparent')
    parser.add_argument('input_folder', help='Input folder containing images')
    parser.add_argument('-o', '--output', required=True, help='Output folder for processed images')
    parser.add_argument('-t', '--threshold', type=int, default=30, 
                       help='Black threshold (0-255, lower = more aggressive)')

    args = parser.parse_args()

    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist")
        sys.exit(1)

    print(f"Removing black backgrounds...")
    print(f"Input: {args.input_folder}")
    print(f"Output: {args.output}")
    print(f"Threshold: {args.threshold}")
    print("-" * 50)

    process_folder(args.input_folder, args.output, args.threshold)

if __name__ == "__main__":
    main()