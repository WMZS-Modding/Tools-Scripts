import json
import argparse
from pathlib import Path

def extract_chatgpt_conversations(mapping):
    """Extract both main (latest) and full conversations from ChatGPT mapping"""
    main_messages = []
    full_messages = []

    role_counts = {}
    
    def follow_latest_path(node_id):
        """Follow the latest path for main conversation"""
        node = mapping.get(node_id)
        if not node:
            return
        
        message = node.get("message")
        if message and should_include_message(message):
            author_role = message.get("author", {}).get("role", "")
            content_parts = get_meaningful_content(message)
            
            if content_parts:
                role_label = "USER" if author_role == "user" else "ASSISTANT"
                for part in content_parts:
                    main_messages.append(f"{role_label}: {part}")

        children = node.get("children", [])
        if children:
            follow_latest_path(children[-1])
    
    def extract_all_messages(node_id, depth=0):
        """Extract all messages including branches for full conversation"""
        node = mapping.get(node_id)
        if not node:
            return
        
        message = node.get("message")
        if message and should_include_message(message):
            author_role = message.get("author", {}).get("role", "")
            content_parts = get_meaningful_content(message)
            
            if content_parts:
                if depth not in role_counts:
                    role_counts[depth] = {"USER": 0, "ASSISTANT": 0}

                role_label_base = "USER" if author_role == "user" else "ASSISTANT"
                role_counts[depth][role_label_base] += 1
                count = role_counts[depth][role_label_base]

                if count > 1:
                    role_label = f"{role_label_base} {count}"
                else:
                    role_label = role_label_base
                
                for part in content_parts:
                    full_messages.append(f"{role_label}: {part}")

        children = node.get("children", [])
        for child_id in children:
            extract_all_messages(child_id, depth + 1)
    
    def should_include_message(message):
        """Check if message should be included in output"""
        author_role = message.get("author", {}).get("role", "")
        if author_role == "system":
            return False
        
        content = message.get("content")
        if not content or content.get("content_type") != "text":
            return False
        
        parts = content.get("parts", [])
        meaningful_parts = [part for part in parts if part and str(part).strip()]
        return len(meaningful_parts) > 0
    
    def get_meaningful_content(message):
        """Extract meaningful content parts from message"""
        content = message.get("content", {})
        parts = content.get("parts", [])
        return [part for part in parts if part and str(part).strip()]

    root_node = next((node for node in mapping.values() if node.get("parent") is None), None)
    if root_node:
        root_id = root_node.get("id")
        follow_latest_path(root_id)
        extract_all_messages(root_id)
    
    return main_messages, full_messages

def count_contexts(messages):
    """Count characters and convert to K contexts"""
    if not messages:
        return 0
    
    text = "\n".join(messages)
    chars = len(text)
    contexts_k = chars // 1000
    
    return contexts_k

def main():
    parser = argparse.ArgumentParser(description="Extract ChatGPT conversations with context counting")
    parser.add_argument("input_json", help="Input JSON exported from ChatGPT")
    parser.add_argument("-o", "--output", help="Output folder", default="chatgpt_conversations")
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

        mapping = conv.get("mapping", {})
        main_messages, full_messages = extract_chatgpt_conversations(mapping)
        
        if not main_messages:
            continue

        main_contexts_k = count_contexts(main_messages)
        full_contexts_k = count_contexts(full_messages)

        with open(file_path, "w", encoding="utf-8") as out:
            out.write(f"Title: {title}\n")
            out.write(f"Main Messages: {len(main_messages)}\n")
            out.write(f"Full Messages: {len(full_messages)}\n")
            out.write(f"Main Contexts: {main_contexts_k}K\n")
            out.write(f"Full Contexts: {full_contexts_k}K\n")
            out.write("=" * 50 + "\n\n")
            out.write("MAIN CONVERSATION (LATEST PATH):\n")
            out.write("-" * 30 + "\n")
            out.write("\n\n".join(main_messages))
            out.write("\n\n" + "=" * 50 + "\n\n")
            out.write("FULL HISTORY (ALL BRANCHES):\n")
            out.write("-" * 25 + "\n")
            out.write("\n\n".join(full_messages))

        print(f"Exported: {file_path}")
        print(f"  Main: {len(main_messages)} messages, {main_contexts_k}K contexts")
        print(f"  Full: {len(full_messages)} messages, {full_contexts_k}K contexts")

if __name__ == "__main__":
    main()