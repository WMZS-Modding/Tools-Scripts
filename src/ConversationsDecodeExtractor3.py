import json
import os
import argparse
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
        description="Extract DeepSeek conversations from JSON to a single TXT file"
    )
    parser.add_argument("input", help="JSON file path (e.g., conversations.json)")
    parser.add_argument("-o", "--output", default="deepseek_conversations.txt", 
                       help="Output TXT filename")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_conversations = []

    for i, conv in enumerate(data, start=1):
        title = conv.get("title", f"untitled_{i}")
        mapping = conv.get("mapping", {})
        
        messages = extract_conversation_text(mapping)
        
        if messages:
            conversation_header = f"\n\n{'='*60}\n{i:03d}. {title}\n{'='*60}\n"
            conversation_text = "\n\n".join(messages)
            all_conversations.append(conversation_header + "\n" + conversation_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(all_conversations))
    
    print(f"Exported {len(all_conversations)} conversations to {args.output}")

if __name__ == "__main__":
    main()