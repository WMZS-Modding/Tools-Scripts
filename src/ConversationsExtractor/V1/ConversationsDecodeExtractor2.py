import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Decode and extract ChatGPT conversations to multiple TXT files")
    parser.add_argument("input_json", help="Input JSON exported from ChatGPT")
    parser.add_argument("-o", "--output", help="Output folder", default="output_folder")
    args = parser.parse_args()

    input_path = Path(args.input_json)
    output_folder = Path(args.output)
    output_folder.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for conv_index, conv in enumerate(data, start=1):
        title = conv.get("title", f"Conversation_{conv_index}")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
        file_path = output_folder / f"{conv_index:03d}_{safe_title}.txt"

        lines = [f"===== {title} =====\n"]
        msg_counter = 0

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
                    lines.append(f"[{msg_counter}] {role_label}: {part}\n")

        with open(file_path, "w", encoding="utf-8") as out:
            out.write("\n".join(lines))

        print(f"Exported {msg_counter} messages to {file_path}")

if __name__ == "__main__":
    main()
