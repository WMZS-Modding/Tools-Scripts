import json
import argparse
from pathlib import Path
import sys

def set_recursion_limit():
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

def find_children(mapping, parent_id):
    children = []
    for node_id, node in mapping.items():
        if node.get("parent") == parent_id:
            children.append(node_id)
    return children

def should_include_message(message):
    author_role = message.get("author", {}).get("role", "")
    if author_role == "system":
        return False

    content = message.get("content")
    if not content:
        return False

    if isinstance(content, str):
        return content.strip() != ""

    if content.get("content_type") != "text":
        return False

    parts = content.get("parts", [])
    meaningful_parts = [part for part in parts if part and str(part).strip()]
    return len(meaningful_parts) > 0

def get_meaningful_content(message):
    content = message.get("content")
    if not content:
        return []

    if isinstance(content, str):
        return [content] if content.strip() else []

    parts = content.get("parts", [])
    return [part for part in parts if part and str(part).strip()]

def count_contexts(messages):
    if not messages:
        return 0

    text = "\n".join(messages)
    chars = len(text)
    contexts_k = chars // 1000
    return contexts_k

def main():
    parser = argparse.ArgumentParser(description="Extract ChatGPT conversations to TXT files with main and full context counts")
    parser.add_argument("input_json", help="Input JSON exported from ChatGPT")
    parser.add_argument("-o", "--output", help="Output folder", default="chatgpt_conversations")
    parser.add_argument("--limit", type=int, default=10000, help="Recursion limit for deep conversations (default: 10000)")

    args = parser.parse_args()

    sys.setrecursionlimit(args.limit)
    print(f"Recursion limit set to: {args.limit}")

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

        main_messages = []
        full_messages = []
        role_counts = {}

        def count_descendants(node_id):
            children = find_children(mapping, node_id)
            if not children:
                return 0

            count = len(children)
            for child_id in children:
                count += count_descendants(child_id)
            return count

        def follow_latest_path(node_id):
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

            children = find_children(mapping, node_id)
            if not children:
                return

            if len(children) == 1:
                follow_latest_path(children[0])
                return

            best_child = None
            best_depth = -1

            for child_id in children:
                depth = count_descendants(child_id)
                if depth > best_depth:
                    best_depth = depth
                    best_child = child_id

            if best_child:
                follow_latest_path(best_child)
            else:
                follow_latest_path(children[-1])

        def extract_all_messages(node_id, depth=0):
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

            children = find_children(mapping, node_id)
            for child_id in children:
                extract_all_messages(child_id, depth + 1)

        root_node = None
        for node_id, node in mapping.items():
            if node.get("parent") is None:
                root_node = node
                break

        if not root_node:
            print(f"Skipping conversation {conv_index}: No root node found")
            continue

        root_id = root_node.get("id")

        follow_latest_path(root_id)
        extract_all_messages(root_id)

        if not main_messages:
            print(f"Skipping conversation {conv_index}: No meaningful messages")
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