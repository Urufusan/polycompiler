#!/usr/bin/env python3

import os
import sys
import base64
from collections import defaultdict


def find_longest_repeating_substring(b64, min_seq_length=6):
    """
    Finds the longest repeating substring in a list of Base64-encoded strings.
    """
    substrings = defaultdict(int)
    longest_substring = ""

    # Extract substrings and track occurrences
    n = len(b64)
    for length in range(min_seq_length, n // 2 + 1):
        for i in range(n - length + 1):
            substr = b64[i : i + length]
            substrings[substr] += 1

            # Prioritize longest substring that appears at least twice
            _l_subst_len = len(longest_substring)
            if substrings[substr] > 1 and len(substr) > _l_subst_len:
                longest_substring = substr

            # Hacky optimization
            if (length - _l_subst_len) > 100:
                return longest_substring if longest_substring else None

    return longest_substring if longest_substring else None


def compress_base64_strings(base64_string, var_name):
    """
    Finds and replaces the longest repeating substring in Base64 strings with a variable.
    """
    substring = find_longest_repeating_substring(base64_string)

    if not substring:
        return None, base64_string  # No optimization found

    optimized_b64 = base64_string.replace(substring, b"'+" + var_name + b"+'")

    return substring, optimized_b64


def compress_all(base64_strings, defs_limit=2):
    _defs = {}
    optimized_b64s = {}
    for _ii, _stringy in enumerate(base64_strings):
        _counter = 0
        while True:
            _def_name = (b"b" if _ii else b"a") + str(_counter).encode()
            repeated_substr, optimized_b64 = compress_base64_strings(_stringy, _def_name)
            if not repeated_substr:
                break

            _stringy = optimized_b64
            optimized_b64s[_ii] = optimized_b64
            _counter += 1
            _defs[_def_name] = repeated_substr
            print(f"Assigning var {_def_name.decode()}...")
            if _counter > defs_limit:
                break

    return _defs, [optimized_b64s[key] for key in sorted(optimized_b64s.keys())]


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <file1> <file2> [output-file]")
        print("Compression can also me utilized with the following example:")
        print(f"DEFLIMIT=15 {os.path.basename(sys.argv[0])} merge.js merge.py merge.py.js -C")
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

    merged = merge_files(python_content, js_content, "-C" in args)

    # Ensure output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Dump merged
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged)
    print(f"Merged files written to {output_path}")


def merge_files(python_content, js_content, compression=False):
    # B64
    _extra = ""
    b64_python_content = base64.b64encode(python_content)
    b64_js_content = base64.b64encode(js_content)

    if compression:
        _defs, optimized_b64s = compress_all((b64_python_content, b64_js_content), defs_limit=int(os.getenv("DEFLIMIT", 3)))
        if not optimized_b64s:
            print("Compression of the merged file failed. The input files may be too small.")
            sys.exit(1)
        str_python_content = optimized_b64s[0].decode(encoding="utf-8")
        str_js_content = optimized_b64s[1].decode(encoding="utf-8")
        _extra = "\n".join(((k + b"='" + v + b"';").decode(encoding="utf-8") for k, v in _defs.items())) + "\n"

    else:
        str_python_content = b64_python_content.decode(encoding="utf-8")
        str_js_content = b64_js_content.decode(encoding="utf-8")

    # eval(["print('Hello, py!')", "console.log('Hello, js!')"][1|0==2])
    return (
        _extra
        + f"""eval(["exec(__import__('base64').b64decode('{str_python_content}').decode(encoding='utf-8',errors='ignore'))","eval(atob('{str_js_content}'))"][1|0==2]);"""
    )


if __name__ == "__main__":
    main()
