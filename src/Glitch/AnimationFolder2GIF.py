import os
import sys
import argparse
from PIL import Image
import glob

def create_gif_from_folder(input_folder, output_gif):
    try:
        image_files = glob.glob(os.path.join(input_folder, '*.png'))
        image_files.sort()
        
        if not image_files:
            print("No PNG files found in input folder")
            return False
        
        print(f"Found {len(image_files)} frames")

        frames = []
        for i, image_file in enumerate(image_files):
            print(f"Loading frame {i+1}/{len(image_files)}: {os.path.basename(image_file)}")
            with Image.open(image_file) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                frames.append(img.copy())

        duration = 33
        loop = 0

        print(f"Creating GIF: {output_gif}")
        print(f"Fixed settings: 30 FPS ({duration}ms per frame), Infinite loop")
        
        frames[0].save(
            output_gif,
            format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=duration,
            loop=loop,
            transparency=0,
            disposal=2
        )
        
        return True
        
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create GIF animation from folder of images (30 FPS, infinite loop)')
    parser.add_argument('input_folder', help='Input folder containing transparent PNG frames')
    parser.add_argument('-o', '--output', required=True, help='Output GIF file path')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist")
        sys.exit(1)
    
    print(f"Creating GIF animation...")
    print(f"Input: {args.input_folder}")
    print(f"Output: {args.output}")
    print(f"Fixed settings: 30 FPS, Infinite loop")
    print("-" * 50)
    
    if create_gif_from_folder(args.input_folder, args.output):
        print(f"\nGIF created successfully: {args.output}")
        size = os.path.getsize(args.output) / (1024 * 1024)
        print(f"File size: {size:.2f} MB")
    else:
        print(f"\nFailed to create GIF")
        sys.exit(1)

if __name__ == "__main__":
    main()