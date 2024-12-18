import unittest
import os
import json
from ChatHistoryToProject import strip_and_split_json

class TestStripAndSplitJson(unittest.TestCase):
    def setUp(self):
        # Test Data
        self.test_cases = {
            "empty-data.json": [],
            "large-data.json": [
                {
                    "title": f"Chat {i}",
                    "mapping": {
                        str(j): {
                            "id": str(j),
                            "message": {
                                "author": {"role": "user" if j % 2 == 0 else "assistant"},
                                "content": {"parts": [f"Message {j}"]}
                            },
                            "parent": str(j - 1) if j > 0 else None,
                            "children": [str(j + 1)] if j < 99 else []
                        }
                        for j in range(100)
                    }
                }
                for i in range(10)
            ],
            "very-large-conversation.json": [
                {
                    "title": "Very Large Conversation",
                    "mapping": {
                        str(i): {
                            "id": str(i),
                            "message": {
                                "author": {"role": "user" if i % 2 == 0 else "assistant"},
                                "content": {"parts": [f"Message {i}"]}
                            },
                            "parent": str(i - 1) if i > 0 else None,
                            "children": [str(i + 1)] if i < 999 else []
                        }
                        for i in range(1000)
                    }
                }
            ],
            "special-characters.json": [
                {
                    "title": "Special Characters Chat",
                    "mapping": {
                        "1": {
                            "id": "1",
                            "message": {
                                "author": {"role": "user"},
                                "content": {"parts": ["Hello, world! 🌍🚀"]}
                            },
                            "parent": None,
                            "children": ["2"]
                        },
                        "2": {
                            "id": "2",
                            "message": {
                                "author": {"role": "assistant"},
                                "content": {"parts": ["Привет! Как дела? 😊"]}
                            },
                            "parent": "1",
                            "children": []
                        }
                    }
                }
            ],
            "exact-split.json": [
                {
                    "title": "Exact Split Chat 1",
                    "mapping": {
                        str(i): {
                            "id": str(i),
                            "message": {
                                "author": {"role": "user" if i % 2 == 0 else "assistant"},
                                "content": {"parts": [f"Exact message {i}"]}
                            },
                            "parent": str(i - 1) if i > 0 else None,
                            "children": [str(i + 1)] if i < 4 else []
                        }
                        for i in range(5)
                    }
                },
                {
                    "title": "Exact Split Chat 2",
                    "mapping": {
                        str(i): {
                            "id": str(i),
                            "message": {
                                "author": {"role": "user" if i % 2 == 0 else "assistant"},
                                "content": {"parts": [f"Exact message {i}"]}
                            },
                            "parent": str(i - 1) if i > 0 else None,
                            "children": [str(i + 1)] if i < 9 else []
                        }
                        for i in range(5, 10)
                    }
                }
            ]
        }

        # Creating files for tests
        self.input_files = []
        for file_name, data in self.test_cases.items():
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.input_files.append(file_name)

        self.output_directory = "test_output"
        self.max_parts = 5  # Default value, can be changed in individual tests

    def test_strip_and_split(self):
        for input_file in self.input_files:
            with self.subTest(input_file=input_file):
                # Use the standard max_parts value for most tests
                current_max_parts = self.max_parts

                # For the "exact-split.json" test, use max_parts=2 to split into 2 parts
                if input_file == "exact-split.json":
                    current_max_parts = 2

                # Run the processing function
                strip_and_split_json(input_file, self.output_directory, current_max_parts)

                # Get the list of output files
                output_files = os.listdir(self.output_directory)

                # Check depending on the input data
                if not self.test_cases[os.path.basename(input_file)]:
                    self.assertFalse(output_files, f"Expected no output files for {input_file}.")
                else:
                    self.assertTrue(output_files, f"Expected output files for {input_file}.")

                for file in output_files:
                    with open(os.path.join(self.output_directory, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.assertTrue(data, f"Output file {file} is empty or invalid.")

                # Clean up output files before the next test
                for file in output_files:
                    os.remove(os.path.join(self.output_directory, file))

    def test_number_of_output_parts(self):
        """
        Checks that the file is split into the specified number of parts.
        """
        input_file = "exact-split.json"
        output_files_expected = 2  # We expect 2 parts

        # Run the function with max_parts=2
        strip_and_split_json(input_file, self.output_directory, output_files_expected)

        # Get the list of output files
        output_files = os.listdir(self.output_directory)

        # Check the number of output files
        self.assertEqual(len(output_files), output_files_expected,
                         f"Expected {output_files_expected} output files, but got {len(output_files)}.")

        # Additional check that each output file contains the correct number of chats
        for file in output_files:
            with open(os.path.join(self.output_directory, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # In "exact-split.json" there are now 2 chats, so each output file should contain 1 chat
                self.assertEqual(len(data), 1, f"Output file {file} should contain 1 chat.")

        # Clean up output files
        for file in output_files:
            os.remove(os.path.join(self.output_directory, file))

    def test_special_characters_encoding(self):
        """
        Checks that special characters and different encodings are handled correctly.
        """
        input_file = "special-characters.json"

        # Run the processing function
        strip_and_split_json(input_file, self.output_directory, self.max_parts)

        # Get the list of output files
        output_files = os.listdir(self.output_directory)

        # Check for the presence of output files
        self.assertTrue(output_files, "Expected output files for data with special characters.")

        # Check the contents of the output files for special characters
        for file in output_files:
            with open(os.path.join(self.output_directory, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for chat in data:
                    for msg in chat["messages"].values():
                        content = " ".join(msg["content"])  # Combine the parts of the message
                        # Check for the presence of special characters
                        self.assertTrue("🌍" in content or "🚀" in content or "😊" in content,
                                        f"The message does not contain the expected special characters: {content}")

        for file in output_files:
            os.remove(os.path.join(self.output_directory, file))

    def tearDown(self):
        # Clear created files
        for input_file in self.input_files:
            if os.path.exists(input_file):
                os.remove(input_file)
        # Clear output dir
        if os.path.exists(self.output_directory):
            for file in os.listdir(self.output_directory):
                os.remove(os.path.join(self.output_directory, file))
            os.rmdir(self.output_directory)

if __name__ == "__main__":
    unittest.main()
