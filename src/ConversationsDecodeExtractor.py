import json
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Decode ChatGPT Export JSON and extract conversations into a single TXT file"
    )
    parser.add_argument("input", help="JSON file path (eg: conversations.json)")
    parser.add_argument("-o", "--output", default="conversations.txt", help="Name of output TXT")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_texts = []

    for i, convo in enumerate(data, start=1):
        title = convo.get("title", f"untitled_{i}")
        items = convo.get("mapping", {})

        contents = []
        for msg in items.values():
            msg_data = msg.get("message")
            if msg_data:
                content_list = msg_data.get("content", [])
                if isinstance(content_list, list):
                    for c in content_list:
                        if c.get("content_type") == "text":
                            parts = c.get("parts", [])
                            if parts:
                                contents.append("\n".join(parts))
                else:
                    if msg_data.get("content", {}).get("content_type") == "text":
                        parts = msg_data["content"].get("parts", [])
                        if parts:
                            contents.append("\n".join(parts))

        if not contents:
            continue

        text_output = f"\n\n=== {i:03d}. {title} ===\n\n" + "\n\n".join(contents)
        all_texts.append(text_output)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("\n\n".join(all_texts))

    print(f"✅ Exported {len(data)} conversations to a file: {output_file}")

if __name__ == "__main__":
    main()
