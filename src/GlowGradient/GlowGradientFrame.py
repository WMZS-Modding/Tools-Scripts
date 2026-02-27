import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math
from collections import Counter

def extract_dominant_colors(image, num_colors=3):
    if image.mode != 'RGB':
        image = image.convert('RGB')

    if image.mode == 'RGBA':
        pixels = []
        width, height = image.size
        for y in range(height):
            for x in range(width):
                r, g, b, a = image.getpixel((x, y))
                if a > 10:
                    pixels.append((r, g, b))
        if not pixels:
            pixels = list(image.getdata())
    else:
        pixels = list(image.getdata())

    color_counter = Counter(pixels)

    most_common = color_counter.most_common(num_colors)

    dominant_colors = [color[0] for color in most_common]

    while len(dominant_colors) < num_colors:
        dominant_colors.append(dominant_colors[-1] if dominant_colors else (255, 255, 255))

    return dominant_colors

def create_color_gradient(colors, steps=100):
    gradient = []

    if len(colors) == 1:
        r, g, b = colors[0]
        for i in range(steps):
            factor = i / steps
            grad_r = int(r * (0.3 + 0.7 * factor))
            grad_g = int(g * (0.3 + 0.7 * factor))
            grad_b = int(b * (0.3 + 0.7 * factor))
            gradient.append((grad_r, grad_g, grad_b))

    else:
        segment_steps = steps // (len(colors) - 1)

        for i in range(len(colors) - 1):
            r1, g1, b1 = colors[i]
            r2, g2, b2 = colors[i + 1]

            for j in range(segment_steps):
                factor = j / segment_steps
                r = int(r1 + (r2 - r1) * factor)
                g = int(g1 + (g2 - g1) * factor)
                b = int(b1 + (b2 - b1) * factor)
                gradient.append((r, g, b))

    return gradient[:steps]

def generate_glow_frames(input_path, output_folder, frame_count=6, frame_size=150, note_name="arrow"):
    try:
        base_image = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    width, height = base_image.size
    FRAME_SIZE = max(width, height, frame_size)

    print("Analyzing image colors...")
    dominant_colors = extract_dominant_colors(base_image, num_colors=3)

    print(f"Detected dominant colors: {dominant_colors}")

    color_gradient = create_color_gradient(dominant_colors, steps=100)

    os.makedirs(output_folder, exist_ok=True)

    for frame_idx in range(frame_count):
        print(f"Generating frame {frame_idx + 1}/{frame_count}...")

        frame = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))

        if frame_count == 6:
            if frame_idx == 0:
                intensity = 0.1
            elif frame_idx == 1:
                intensity = 0.5
            elif frame_idx == 2:
                intensity = 1.0
            elif frame_idx == 3:
                intensity = 0.7
            elif frame_idx == 4:
                intensity = 0.3
            elif frame_idx == 5:
                intensity = 0.1
        else:
            intensity = math.sin((frame_idx / (frame_count - 1)) * math.pi)

        max_glow_radius = min(FRAME_SIZE // 3, 50)
        glow_radius = int(max_glow_radius * intensity)

        if glow_radius > 0:
            glow_layer = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(glow_layer)

            center_x, center_y = FRAME_SIZE // 2, FRAME_SIZE // 2

            for ring_idx in range(glow_radius, 0, -1):
                color_idx = min(int((ring_idx / glow_radius) * len(color_gradient)), len(color_gradient) - 1)
                r, g, b = color_gradient[color_idx]

                opacity = int(200 * intensity * (ring_idx / glow_radius))

                draw.ellipse([
                    center_x - ring_idx, center_y - ring_idx,
                    center_x + ring_idx, center_y + ring_idx
                ], fill=(r, g, b, opacity))

            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=3))

            frame = Image.alpha_composite(frame, glow_layer)

        paste_x = (FRAME_SIZE - width) // 2
        paste_y = (FRAME_SIZE - height) // 2

        if intensity > 0.5:
            brightener = ImageEnhance.Brightness(base_image)
            brightened = brightener.enhance(1.0 + (intensity - 0.5))
            frame.paste(brightened, (paste_x, paste_y), brightened)
        else:
            frame.paste(base_image, (paste_x, paste_y), base_image)

        frame_filename = os.path.join(output_folder, f"frame_{frame_idx:02d}.png")
        frame.save(frame_filename, "PNG")

    if frame_count > 0:
        create_sprite_sheet(output_folder, frame_count, FRAME_SIZE)
        generate_single_note_xml(output_folder, frame_count, FRAME_SIZE, sprite_sheet_name="sprite_sheet.png", note_name=note_name)

    print(f"\nDone! Generated {frame_count} frames in '{output_folder}'")
    print(f"Dominant colors used: {dominant_colors}")

def create_sprite_sheet(folder_path, frame_count, frame_size):
    sprite_sheet = Image.new("RGBA", (frame_size * frame_count, frame_size), (0, 0, 0, 0))

    for i in range(frame_count):
        frame_path = os.path.join(folder_path, f"frame_{i:02d}.png")
        if os.path.exists(frame_path):
            frame = Image.open(frame_path)
            sprite_sheet.paste(frame, (i * frame_size, 0))

    sprite_sheet.save(os.path.join(folder_path, "sprite_sheet.png"))
    print(f"Created sprite sheet: {os.path.join(folder_path, 'sprite_sheet.png')}")

def generate_single_note_xml(output_folder, frame_count, frame_size, sprite_sheet_name="sprite_sheet.png", note_name="arrow"):
    xml_content = ['<?xml version="1.0" encoding="utf-8"?>']
    xml_content.append(f'<TextureAtlas imagePath="{sprite_sheet_name}">\n')

    for i in range(frame_count):
        frame_name = f"{note_name}{i:04d}"
        x_position = i * frame_size
        y_position = 0

        xml_content.append(
            f'    <SubTexture name="{frame_name}" '
            f'x="{x_position}" y="{y_position}" '
            f'width="{frame_size}" height="{frame_size}"/>\n'
        )

    xml_content.append('</TextureAtlas>')

    xml_path = os.path.join(output_folder, f"{note_name}_assets.xml")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(''.join(xml_content))

    print(f"Generated XML: {xml_path}")
    return xml_path

def main():
    parser = argparse.ArgumentParser(description="Generate glow gradient animation frames from any image. " "Automatically detects image colors.")
    parser.add_argument("-i", "--input", required=True, help="Input image file path")
    parser.add_argument("-o", "--output", required=True, help="Output folder for frames")
    parser.add_argument("-f", "--frames", type=int, default=6, help="Number of frames to generate (default: 6, FNF standard)")
    parser.add_argument("--glow-intensity", type=float, default=1.0, help="Overall glow intensity multiplier (default: 1.0)")
    parser.add_argument("--max-radius", type=int, default=0, help="Maximum glow radius in pixels (0 for auto)")
    parser.add_argument("--size", type=int, default=150, help="Output frame size in pixels (default: 150)")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        sys.exit(1)

    if args.frames < 2:
        print("Error: Need at least 2 frames for animation")
        sys.exit(1)

    print(f"Generating {args.frames} glow frames for: {args.input}")
    print(f"Output folder: {args.output}")

    generate_glow_frames(args.input, args.output, args.frames, frame_size=args.size)

if __name__ == "__main__":
    main()