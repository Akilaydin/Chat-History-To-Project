import json
import os

def strip_and_split_json(input_file, output_directory, max_parts):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    def process_mapping(mapping):
        stripped_mapping = {}
        for key, value in mapping.items():
            if value.get("message") and value["message"].get("content"):
                content_parts = value["message"]["content"].get("parts", [])
                stripped_mapping[key] = {
                    "id": value["id"],
                    "parent": value.get("parent"),
                    "children": value.get("children", []),
                    "content": content_parts,
                    "author": value["message"]["author"]["role"]
                }
        return stripped_mapping

    stripped_data = []
    for chat in data:
        stripped_data.append({
            "title": chat["title"],
            "messages": process_mapping(chat["mapping"])
        })

    total_size = sum(len(json.dumps(chat).encode('utf-8')) for chat in stripped_data)
    max_file_size_bytes = total_size // max_parts

    part_number = 1
    current_part = []
    current_part_size = 0

    for chat in stripped_data:
        serialized_chat = json.dumps(chat)
        chat_size = len(serialized_chat.encode('utf-8'))

        if current_part_size + chat_size > max_file_size_bytes:
            write_part_to_file(current_part, output_directory, part_number)
            part_number += 1
            current_part = []
            current_part_size = 0

        current_part.append(chat)
        current_part_size += chat_size

    if current_part:
        write_part_to_file(current_part, output_directory, part_number)

    print("JSON file stripped and split successfully.")

def write_part_to_file(part_data, output_directory, part_number):
    output_path = os.path.join(output_directory, f"part_{part_number}.json")
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(part_data, output_file, indent=4, ensure_ascii=False)
    print(f"Written part {part_number} to {output_path}")

# Example usage
if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(__file__), "conversations.json")  # Input JSON in the same folder as the script
    output_directory = os.path.join(os.path.dirname(__file__), "Output")        # Output folder in the same location as the script
    max_parts = 19                                                               # Target maximum number of output files

    strip_and_split_json(input_file, output_directory, max_parts)
