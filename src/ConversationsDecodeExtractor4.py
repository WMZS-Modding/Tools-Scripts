import json
import os
import argparse
import re
from collections import deque

def extract_conversation_text(mapping):
    """Extract conversation text from DeepSeek's mapping structure"""
    root_node = None
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            root_node = node
            break
    
    if not root_node:
        return []
    
    messages = []
    stack = deque(root_node.get("children", []))
    
    while stack:
        node_id = stack.popleft()
        node = mapping.get(node_id)
        if not node:
            continue
        
        if "children" in node:
            stack.extendleft(reversed(node["children"]))
        
        message_data = node.get("message")
        if message_data and "fragments" in message_data:
            for fragment in message_data["fragments"]:
                msg_type = fragment.get("type", "")
                content = fragment.get("content", "")
                
                if content.strip():
                    role = "USER" if msg_type == "REQUEST" else "ASSISTANT"
                    messages.append(f"{role}: {content}")
    
    return messages

def main():
    parser = argparse.ArgumentParser(
        description="Extract DeepSeek conversations from JSON to multiple TXT files"
    )
    parser.add_argument("input", help="JSON file path (e.g., conversations.json)")
    parser.add_argument("-o", "--output", default="deepseek_conversations", 
                       help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    exported_count = 0

    for i, conv in enumerate(data, start=1):
        title = conv.get("title", f"untitled_{i}")
        mapping = conv.get("mapping", {})
        
        messages = extract_conversation_text(mapping)
        
        if not messages:
            continue

        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
        safe_title = safe_title[:50] or f"conversation_{i}"
        
        filename = f"{i:03d}_{safe_title}.txt"
        filepath = os.path.join(args.output, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Messages: {len(messages)}\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n\n".join(messages))

        exported_count += 1

    print(f"Exported {exported_count} conversations to '{args.output}' folder")

if __name__ == "__main__":
    main()