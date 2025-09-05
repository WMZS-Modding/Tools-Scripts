import json
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Extract ChatGPT conversations JSON into multiple TXT files"
    )
    parser.add_argument("input", help="JSON file path (eg: conversations.json)")
    parser.add_argument("-o", "--output", default="conversations_txt", help="Folder to save the TXT files")
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output

    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0

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

        text_output = f"=== {title} ===\n\n" + "\n\n".join(contents)

        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:100]
        filename = os.path.join(output_dir, f"{i:03d}_{safe_title}.txt")

        with open(filename, "w", encoding="utf-8") as out:
            out.write(text_output)

        count += 1

    print(f"✅ Exported {count} conversations to folder: {output_dir}")

if __name__ == "__main__":
    main()
