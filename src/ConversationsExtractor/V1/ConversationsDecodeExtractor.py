import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Decode and extract ChatGPT conversations to a single TXT file")
    parser.add_argument("input_json", help="Input JSON exported from ChatGPT")
    parser.add_argument("-o", "--output", help="Output TXT file", default="output.txt")
    args = parser.parse_args()

    input_path = Path(args.input_json)
    output_path = Path(args.output)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_texts = []
    msg_counter = 0

    for conv in data:
        title = conv.get("title", "Untitled")
        all_texts.append(f"===== {title} =====\n")

        for item in conv.get("mapping", {}).values():
            message = item.get("message")
            if not message:
                continue

            content = message.get("content")
            if not content:
                continue

            if content.get("content_type") == "text":
                parts = content.get("parts", [])
                if not parts:
                    continue
                role = message.get("author", {}).get("role", "")
                role_label = "USER" if role == "user" else "ASSISTANT" if role == "assistant" else role.upper()

                for part in parts:
                    msg_counter += 1
                    all_texts.append(f"[{msg_counter}] {role_label}: {part}\n")

        all_texts.append("\n")

    output_text = "\n".join(all_texts)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(output_text)

    print(f"Done! Exported {msg_counter} messages to {output_path}")

if __name__ == "__main__":
    main()
