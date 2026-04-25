import os
import math
import argparse
from PIL import Image

def create_splash_frame(base_image, frame_idx, total_frames, speed=1.0, burst_count=8, frame_size=200):
    progress = frame_idx / (total_frames - 1) if total_frames > 1 else 0

    progress = 1.0 - math.pow(1.0 - progress, 1.5)
    progress = progress * speed
    if progress > 1.0:
        progress = 1.0

    canvas = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    center_x, center_y = frame_size // 2, frame_size // 2

    img_width, img_height = base_image.size

    is_vertical = img_height > img_width

    for i in range(burst_count):
        target_angle = (i / burst_count) * math.pi * 2

        max_distance = frame_size * 0.6
        distance = max_distance * progress

        x = center_x + math.cos(target_angle) * distance
        y = center_y + math.sin(target_angle) * distance

        if progress < 0.7:
            scale = 0.2 + (progress / 0.7) * 0.8
        else:
            scale = 1.0 - ((progress - 0.7) / 0.3) * 0.5

        if progress < 0.8:
            alpha = int(255 * (progress / 0.8))
        else:
            alpha = int(255 * (1.0 - (progress - 0.8) / 0.2))

        new_size = int(max(img_width, img_height) * scale)
        if new_size > 1:
            rotated = base_image.copy()

            if is_vertical:
                target_deg = math.degrees(target_angle)

                rotation_needed = target_deg + 90

                rotated = rotated.rotate(-rotation_needed, expand=True, center=(rotated.width//2, rotated.height//2), resample=Image.Resampling.BICUBIC)
            else:
                target_deg = math.degrees(target_angle)
                rotation_needed = target_deg

                rotated = rotated.rotate(-rotation_needed, expand=True, center=(rotated.width//2, rotated.height//2), resample=Image.Resampling.BICUBIC)

            rotated.thumbnail((new_size, new_size), Image.Resampling.LANCZOS)

            if rotated.mode == 'RGBA':
                pixels = rotated.load()
                for py in range(rotated.height):
                    for px in range(rotated.width):
                        r, g, b, a = pixels[px, py]
                        if a > 0:
                            brightness = 1.0 + (1.0 - abs(progress - 0.5) * 2) * 0.5
                            r = min(255, int(r * brightness))
                            g = min(255, int(g * brightness))
                            b = min(255, int(b * brightness))
                            pixels[px, py] = (r, g, b, a)

            if alpha < 255 and rotated.mode == 'RGBA':
                pixels = rotated.load()
                for py in range(rotated.height):
                    for px in range(rotated.width):
                        r, g, b, a = pixels[px, py]
                        if a > 0:
                            new_alpha = int(a * alpha / 255)
                            pixels[px, py] = (r, g, b, new_alpha)

            paste_x = int(x - rotated.width // 2)
            paste_y = int(y - rotated.height // 2)

            if paste_x + rotated.width > 0 and paste_x < frame_size:
                canvas.paste(rotated, (paste_x, paste_y), rotated)

    return canvas

def generate_splash_frames(input_path, output_folder, frame_count=6, speed=1.0, burst_count=8, frame_size=200):
    base_image = Image.open(input_path).convert("RGBA")

    os.makedirs(output_folder, exist_ok=True)

    frames = []
    for frame_idx in range(frame_count):
        print(f"Generating frame {frame_idx + 1}/{frame_count}...")

        frame = create_splash_frame(
            base_image, frame_idx, frame_count, 
            speed=speed, burst_count=burst_count, 
            frame_size=frame_size
        )

        frame_path = os.path.join(output_folder, f"splash_{frame_idx:02d}.png")
        frame.save(frame_path)
        frames.append(frame)

    sprite_sheet = Image.new("RGBA", (frame_size * frame_count, frame_size), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sprite_sheet.paste(frame, (i * frame_size, 0))

    sprite_sheet_path = os.path.join(output_folder, "splash_sheet.png")
    sprite_sheet.save(sprite_sheet_path)

    print(f"\nGenerated {frame_count} frames in '{output_folder}'")
    print(f"   Sprite sheet: {sprite_sheet_path}")
    print(f"   Dimensions: {frame_size * frame_count}x{frame_size}")

    generate_splash_xml(output_folder, frame_count, frame_size)

def generate_splash_xml(output_folder, frame_count, frame_size):
    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>']
    xml_lines.append('<TextureAtlas imagePath="splash_sheet.png">')

    for i in range(frame_count):
        frame_name = f"splash{i:04d}"
        x_pos = i * frame_size
        y_pos = 0

        xml_lines.append(
            f'    <SubTexture name="{frame_name}" '
            f'x="{x_pos}" y="{y_pos}" '
            f'width="{frame_size}" height="{frame_size}"/>'
        )

    xml_lines.append('</TextureAtlas>')

    xml_path = os.path.join(output_folder, "splash_assets.xml")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))

    print(f"   XML: {xml_path}")

def main():
    parser = argparse.ArgumentParser(description="Create FNF note splash animations")
    parser.add_argument("-i", "--input", required=True, help="Input image path")
    parser.add_argument("-o", "--output", required=True, help="Output folder")
    parser.add_argument("-f", "--frames", type=int, default=6, help="Number of frames (default: 6)")
    parser.add_argument("--speed", type=float, default=1.0, help="Animation speed multiplier (default: 1.0)")
    parser.add_argument("--count", type=int, default=8, help="Number of burst directions (4,6,8, default: 8)")
    parser.add_argument("--size", type=int, default=200, help="Frame size in pixels (default: 200)")
    args = parser.parse_args()

    generate_splash_frames(args.input, args.output, args.frames, args.speed, args.count, args.size)

if __name__ == "__main__":
    main()