import os
import colorsys
from PIL import Image, ImageDraw
from collections import Counter

def analyze_frame_colors_for_gradient(image, num_colors=3):
    if image.mode != 'RGB':
        rgb_image = image.convert('RGB')
    else:
        rgb_image = image

    pixels = list(rgb_image.getdata())
    color_counter = Counter(pixels)

    color_samples = []
    for color, count in color_counter.most_common(50):
        r, g, b = color
        if not (r < 40 and g < 40 and b < 40):
            color_samples.extend([color] * min(10, count))
            if len(color_samples) > 100:
                break

    if not color_samples:
        return [(255, 150, 0), (255, 100, 0), (255, 50, 0)]

    color_samples.sort(key=lambda c: colorsys.rgb_to_hsv(*c)[2])

    gradient_colors = []
    step = max(1, len(color_samples) // num_colors)
    for i in range(0, len(color_samples), step):
        if len(gradient_colors) >= num_colors:
            break
        gradient_colors.append(color_samples[i])

    return gradient_colors

def create_color_gradient(colors, steps=100):
    if len(colors) == 1:
        return [colors[0]] * steps

    gradient = []
    segments = len(colors) - 1
    steps_per_segment = steps // segments

    for i in range(segments):
        r1, g1, b1 = colors[i]
        r2, g2, b2 = colors[i + 1]

        for j in range(steps_per_segment):
            t = j / steps_per_segment
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            gradient.append((r, g, b))

    return gradient[:steps]

def replace_black_with_gradient(frame_path, frame_index, total_frames):
    frame = Image.open(frame_path).convert("RGBA")
    width, height = frame.size

    if frame_index == 0 or frame_index == total_frames - 1:
        return frame

    gradient_colors = analyze_frame_colors_for_gradient(frame, num_colors=3)
    gradient = create_color_gradient(gradient_colors, steps=100)

    black_mask = Image.new('L', (width, height), 0)
    frame_data = frame.load()
    mask_data = black_mask.load()

    for y in range(height):
        for x in range(width):
            r, g, b, a = frame_data[x, y]
            if a > 10 and (r < 50 and g < 50 and b < 50):
                mask_data[x, y] = 255

    center_x, center_y = width // 2, height // 2
    max_distance = ((center_x**2 + center_y**2)**0.5) * 0.8

    for y in range(height):
        for x in range(width):
            if mask_data[x, y] > 0:
                dx, dy = x - center_x, y - center_y
                distance = (dx**2 + dy**2)**0.5

                gradient_idx = min(int((distance / max_distance) * len(gradient)), len(gradient)-1)

                r, g, b = gradient[gradient_idx]

                original_alpha = frame_data[x, y][3]
                frame_data[x, y] = (r, g, b, original_alpha)

    return frame

def process_frames_with_gradient(frames_folder):
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.startswith("frame_") and f.endswith(".png")])

    total_frames = len(frame_files)
    print(f"Found {total_frames} frames")

    for i, frame_file in enumerate(frame_files):
        frame_path = os.path.join(frames_folder, frame_file)

        print(f"Processing frame {i}/{total_frames-1}: {frame_file}")

        if i == 0 or i == total_frames - 1:
            print("  Keeping black (first/last frame)")
            continue

        print(f"  Applying gradient...")

        frame = Image.open(frame_path).convert("RGBA")
        colors = analyze_frame_colors_for_gradient(frame, num_colors=3)
        print(f"  Gradient colors: {colors}")

        new_frame = replace_black_with_gradient(frame_path, i, total_frames)
        new_frame.save(frame_path)

def create_gradient_test_frame():
    img = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([60, 60, 90, 90], fill=(0, 0, 0, 255))
    draw.rectangle([20, 20, 50, 50], fill=(0, 0, 0, 255))
    draw.rectangle([100, 100, 130, 130], fill=(0, 0, 0, 255))
    draw.polygon([75, 20, 100, 50, 50, 50], fill=(0, 0, 0, 255))

    draw.rectangle([40, 100, 110, 130], fill=(255, 100, 0, 255))
    draw.rectangle([50, 40, 100, 90], fill=(255, 200, 100, 255))

    img.save("TEST_gradient_frame.png")
    print("Created TEST_gradient_frame.png")

    test_folder = "test_gradient"
    os.makedirs(test_folder, exist_ok=True)
    img.save(os.path.join(test_folder, "frame_00.png"))

    process_frames_with_gradient(test_folder)

    print("\nCheck test_gradient/frame_00.png")
    print("Black shapes should have gradient: center=brighter, edges=darker")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        process_frames_with_gradient(sys.argv[1])
    else:
        print("\nUsage: python analyze_and_gradient_replace.py <frames_folder>")
        print("\nFor each frame:")
        print("1. Analyze frame's colors")
        print("2. Create gradient from those colors")
        print("3. Replace black pixels with radial gradient")
        print("   - Center: brighter colors")
        print("   - Edges: darker colors")