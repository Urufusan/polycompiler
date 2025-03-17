#!/usr/bin/env python3

import os
import sys
import base64


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print("Usage: polycompiler <file1> <file2> [output-file]")
        sys.exit(1)

    file1_path = args[0]
    file2_path = args[1]
    output_path = args[2] if len(args) > 2 else "out/result.py.js"

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("Error: One or more input files do not exist.")
        sys.exit(1)

    # Get file extensions
    ext1 = os.path.splitext(file1_path)[1].lower()
    ext2 = os.path.splitext(file2_path)[1].lower()

    def is_python(ext):
        return ext in [".py"]

    def is_javascript(ext):
        return ext in [".js", ".cjs", ".mjs"]

    has_python = is_python(ext1) or is_python(ext2)
    has_js = is_javascript(ext1) or is_javascript(ext2)

    if not (has_python and has_js):
        print(f"Merging {ext1[1:]} and {ext2[1:]} is not supported. Only Python and JavaScript files can be merged.")
        sys.exit(1)

    with open(file1_path, "r") as f:
        content1 = f.read().encode(encoding="utf-8")
    with open(file2_path, "r") as f:
        content2 = f.read().encode(encoding="utf-8")

    # Determine which file is Python and which is JavaScript
    python_content = content1 if is_python(ext1) else content2
    js_content = content1 if is_javascript(ext1) else content2

    merged = merge_files(python_content, js_content)

    # Ensure output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Dump merged
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged)
    print(f"Merged files written to {output_path}")


def merge_files(python_content, js_content):
    # B64
    encoded_python_content = base64.b64encode(python_content).decode(encoding="utf-8")
    encoded_js_content = base64.b64encode(js_content).decode(encoding="utf-8")

    # eval(["print('Hello, py!')", "console.log('Hello, js!')"][1|0==2])
    return f"""eval(["exec(__import__('base64').b64decode('{encoded_python_content}').decode(encoding='utf-8',errors='ignore'))","eval(atob('{encoded_js_content}'))"][1|0==2])"""


if __name__ == "__main__":
    main()
