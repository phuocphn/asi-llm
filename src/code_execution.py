import ast
import re

import traceback


def parse_and_execute_python_code(file_path: str) -> [bool, str, str]:
    """
    Parses the Python code in a text file, executes it, and retrieves the assertion message if any assertion fails.

    Args:
        file_path (str): Path to the text file containing Python code.

    Returns:
        bool: True if all assertions passed, False otherwise.
        str: The executed code.
        str: Assertion message if an assertion fails, otherwise "All assertions passed."
    """

    code = ""

    try:
        # Read the Python code from the file
        with open(file_path, "r") as file:
            code = file.read()

        # Extract the last Python code block wrapped inside ```python and ```
        matches = re.findall(r"```python(.*?)```", code, re.DOTALL)
        if matches:
            code = matches[-1].strip()  # Use the last match

        # Parse the code to ensure it's valid Python
        ast.parse(code)

        # Execute the code
        exec_globals = {}
        exec(code, exec_globals)

        return True, code, "All assertions passed."

    except Exception as e:
        # Capture the full traceback as a string
        tb = traceback.format_exc()

        # Extract the line number and content from the traceback
        tb_lines = tb.splitlines()
        code_lines = code.splitlines()
        enhanced_tb = tb  # Start with the original traceback

        for line in tb_lines:
            if "File" in line and "<string>" in line:
                parts = line.split(",")
                line_number = int(parts[1].strip().split(" ")[1])
                # Safely get the line content from the dynamically executed code
                if 0 < line_number <= len(code_lines):
                    line_content = code_lines[line_number - 1].strip()
                    enhanced_tb += f"\n{line_number}: {line_content}"

        return False, code, enhanced_tb


# Example usage
if __name__ == "__main__":
    file_path = "outputs/direct.code/llama3.3:70b/HL3/response_0.log"  # Replace with the actual file path
    _, _, result = parse_and_execute_python_code(file_path)
    print("Execution Result:")
    print(result)
    print("-----")
