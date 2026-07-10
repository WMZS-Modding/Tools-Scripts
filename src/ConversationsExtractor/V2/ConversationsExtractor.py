import json
import os
import argparse
import re
import sys

def set_recursion_limit():
    """Set recursion limit based on command line argument if provided"""
    if '--limit' in sys.argv:
        limit_index = sys.argv.index('--limit')
        if limit_index + 1 < len(sys.argv):
            try:
                new_limit = int(sys.argv[limit_index + 1])
                original_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(new_limit)
                print(f"Recursion limit changed from {original_limit} to {new_limit}")
            except ValueError:
                print(f"Warning: Invalid recursion limit value, using default")
    else:
        sys.setrecursionlimit(10000)
        print(f"Recursion limit set to: {sys.getrecursionlimit()}")

set_recursion_limit()

def extract_latest_conversation_text(mapping):
    """Extract conversation text taking only the path that continues the conversation"""
    all_messages = []

    current_node_id = 'root'

    while current_node_id:
        node = mapping.get(current_node_id)
        if not node:
            break

        message_data = node.get("message")
        if message_data and "fragments" in message_data:
            for fragment in message_data["fragments"]:
                msg_type = fragment.get("type", "")
                content = fragment.get("content", "")
                
                if content.strip():
                    role = "USER" if msg_type == "REQUEST" else "ASSISTANT"
                    all_messages.append(f"{role}: {content}")

        children = node.get("children", [])
        if not children:
            break

        best_child = None
        best_depth = -1

        for child_id in children:
            depth = count_descendants(mapping, child_id)
            if depth > best_depth:
                best_depth = depth
                best_child = child_id

        if best_child:
            current_node_id = best_child
        else:
            current_node_id = children[-1]

    return all_messages

def count_descendants(mapping, node_id):
    """Count how many descendants a node has"""
    node = mapping.get(node_id)
    if not node:
        return 0

    children = node.get("children", [])
    if not children:
        return 0

    count = len(children)
    for child_id in children:
        count += count_descendants(mapping, child_id)

    return count

def extract_all_conversation_text(mapping):
    """Extract ALL conversation text including all edits/regenerations with numbering"""
    all_messages = []
    processed_nodes = set()

    nodes_with_timestamps = []
    
    def collect_all_nodes(node_id, depth=0):
        """Collect all nodes with their timestamps"""
        if node_id in processed_nodes:
            return
        processed_nodes.add(node_id)
        
        node = mapping.get(node_id)
        if not node:
            return

        timestamp = None
        message_data = node.get("message")
        if message_data:
            timestamp = message_data.get("inserted_at")

        nodes_with_timestamps.append((node_id, depth, timestamp))

        children = node.get("children", [])
        for child_id in children:
            collect_all_nodes(child_id, depth + 1)

    collect_all_nodes('root')

    nodes_with_timestamps.sort(key=lambda x: (x[1], x[2] if x[2] else ''))

    role_counts = {}

    for node_id, depth, timestamp in nodes_with_timestamps:
        node = mapping.get(node_id)
        if not node:
            continue

        message_data = node.get("message")
        if message_data and "fragments" in message_data:
            for fragment in message_data["fragments"]:
                msg_type = fragment.get("type", "")
                content = fragment.get("content", "")

                if content.strip():
                    role = "USER" if msg_type == "REQUEST" else "ASSISTANT"

                    if depth not in role_counts:
                        role_counts[depth] = {"USER": 0, "ASSISTANT": 0}

                    role_counts[depth][role] += 1
                    count = role_counts[depth][role]

                    if count > 1:
                        role_label = f"{role} {count}"
                    else:
                        role_label = role
                    
                    all_messages.append(f"{role_label}: {content}")

    return all_messages

def count_contexts(messages):
    """Count characters and convert to K contexts"""
    if not messages:
        return 0
    
    text = "\n".join(messages)
    chars = len(text)
    contexts_k = chars // 1000
    
    return contexts_k

def main():
    parser = argparse.ArgumentParser(
        description="Extract DeepSeek conversations to TXT files with main and full context counts"
    )
    parser.add_argument("input", help="JSON file path (e.g., conversations.json)")
    parser.add_argument("-o", "--output", default="deepseek_conversations", help="Output directory")
    parser.add_argument("--limit", type=int, help="Set recursion limit for deep conversations")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    exported_count = 0

    for i, conv in enumerate(data, start=1):
        title = conv.get("title", f"untitled_{i}")
        mapping = conv.get("mapping", {})

        main_messages = extract_latest_conversation_text(mapping)
        full_messages = extract_all_conversation_text(mapping)
        
        if not main_messages:
            continue

        main_contexts_k = count_contexts(main_messages)
        full_contexts_k = count_contexts(full_messages)

        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
        safe_title = safe_title[:50] or f"conversation_{i}"
        
        filename = f"{i:03d}_{safe_title}.txt"
        filepath = os.path.join(args.output, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Main Messages: {len(main_messages)}\n")
            f.write(f"Full Messages: {len(full_messages)}\n")
            f.write(f"Main Contexts: {main_contexts_k}K\n")
            f.write(f"Full Contexts: {full_contexts_k}K\n")
            f.write("=" * 50 + "\n\n")
            f.write("MAIN CONVERSATION (LATEST PATH):\n")
            f.write("-" * 30 + "\n")
            f.write("\n\n".join(main_messages))
            f.write("\n\n" + "=" * 50 + "\n\n")
            f.write("FULL HISTORY (ALL EDITS/REGENERATIONS):\n")
            f.write("-" * 40 + "\n")
            f.write("\n\n".join(full_messages))

        exported_count += 1

    print(f"Exported {exported_count} conversations to '{args.output}' folder")
    print("Main Contexts: Latest conversation path only")
    print("Full Contexts: All messages with numbering")

if __name__ == "__main__":
    main()