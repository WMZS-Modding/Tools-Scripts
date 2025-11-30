def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def generate_gradient(color1, color2, steps):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    r_step = (rgb2[0] - rgb1[0]) / (steps - 1)
    g_step = (rgb2[1] - rgb1[1]) / (steps - 1)
    b_step = (rgb2[2] - rgb1[2]) / (steps - 1)

    gradient = []
    for i in range(steps):
        r = int(rgb1[0] + (r_step * i))
        g = int(rgb1[1] + (g_step * i))
        b = int(rgb1[2] + (b_step * i))
        gradient.append(rgb_to_hex((r, g, b)))
    
    return gradient

def main():
    print("=== Gradient Color Generator ===\n")

    color_input = input("Color input (hex format): ").strip()
    color_output = input("Color output (hex format): ").strip()

    while True:
        try:
            num_colors = int(input("How many color codes do you want to your gradient color? (Maximum: 32): "))
            if 2 <= num_colors <= 32:
                break
            else:
                print("Please enter a number between 2 and 32.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nGradient from {color_input} to {color_output}:")
    gradient = generate_gradient(color_input, color_output, num_colors)
    
    for i, color in enumerate(gradient, 1):
        print(color)

if __name__ == "__main__":
    main()