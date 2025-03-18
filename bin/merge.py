#!/usr/bin/env python3

import os
import sys
import base64
import zlib


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <file1> <file2> [output-file]")
        print("Compression can also me utilized with the following example:")
        print(f"{os.path.basename(sys.argv[0])} merge.js merge.py merge.py.js -C")
        sys.exit(1)

    use_compression = "-C" in args
    if use_compression:
        args.remove("-C")

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
        print(
            f"Merging {ext1[1:]} and {ext2[1:]} is not supported. Only Python and JavaScript files can be merged."
        )
        sys.exit(1)

    with open(file1_path, "r") as f:
        content1 = f.read().encode(encoding="utf-8")
    with open(file2_path, "r") as f:
        content2 = f.read().encode(encoding="utf-8")

    # Determine which file is Python and which is JavaScript
    python_content = content1 if is_python(ext1) else content2
    js_content = content1 if is_javascript(ext1) else content2

    merged = merge_files(python_content, js_content, use_compression)

    # Ensure output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Dump merged
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged)
    print(f"Merged files written to {output_path}")


def merge_files(python_content, js_content, compression=False):
    if compression:
        py_b = zlib.compress(python_content, 9)
        js_b = zlib.compress(js_content, 9)
        # TODO: figure out compression for JS on Node and Web
    else:
        py_b = python_content
        js_b = js_content

    str_python_content = base64.b64encode(py_b).decode(encoding="utf-8")
    str_js_content = base64.b64encode(js_b).decode(encoding="utf-8")

    # eval(["print('Hello, py!')", "console.log('Hello, js!')"][1|0==2])
    # await new Response((await new Blob([Uint8Array.from(atob("eNorKMrMK9FQ8kjNycnXUQjPL8pJUVTSBABZLgcs"),c=>c.charCodeAt())]).stream().pipeThrough(new DecompressionStream("deflate")))).text();
    if compression:
        return f"""eval(["exec(__import__('zlib').decompress(__import__('base64').b64decode('{str_python_content}')).decode(encoding='utf-8',errors='ignore'))","(async () => eval(await new Response((await new Blob([Uint8Array.from(atob('{str_js_content}'), c => c.charCodeAt())]).stream().pipeThrough(new DecompressionStream('deflate')))).text()))()"][1|0==2]);"""
    else:
        return f"""eval(["exec(__import__('base64').b64decode('{str_python_content}').decode(encoding='utf-8',errors='ignore'))","eval(atob('{str_js_content}'))"][1|0==2]);"""


if __name__ == "__main__":
    main()
