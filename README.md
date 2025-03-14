# Polycompile

An experimental project to attempt to merge arbitrary Python and JS code into one source file.

For example, the following code prints `Hello JS` when run with Node, and `Hello Python` when run with Python 3.

```py
1 // (lambda: exec("print('Hello Python')", globals()))()
lambda: eval("console.log('Hello JS')")
```

## Installation & Use

### Install `polycompile` on NPM:

```bash
npm i polycompile
```

### Merge your files

Now, run the `polycompile` command, providing the path to a JS file, a Python file, and an optional result file path.

- **When the output is run with Node.js**: It will run your JS file
- **When the output is run with Python**: It will run your Python file

```bash
polycompile in.js in.py out.js.py
```

> **🚧 WIP**: The current file convention for Polycompile is either `.js.py` or `.py.js` (ideally in alphabetical order, so `.js.py`). This is becuase Node refuses to parse files of "nonexistent" extensions, so it has to end in a pre-existing file extension.

### Test it out

First, running it in Node should execute your JS

```bash
node out.js.py
```

And, running it with `python3` will execute the Python

```bash
python3 out.js.py
```

## Why Polycompile?

The best answer for this is honestly "for fun". However, it could also possibly be a possible solution for a single file that can be targeted to both Python and JS audiences (who may perhaps not have the other installed).

## How does this work?

Let's work through this code to see how Polycompile works:

```py
1 // (lambda: exec("print('Hello Python')", globals()))()
lambda: eval("console.log('Hello JS')")
```

### Running the Output in Python

First, let's consider what happens when we run this in Python:

- The first statement in of itself returns nothing, but the lambda function is executed, containing the `eval` with our target code
- The second statement is not run at all, since the lambda expression is not called. Thus, the "incorrect" JS code in the `eval` is never run

This effectively only runs the Python code.

### Running the Output in JS

Now, let's consider what happens if you run the code in JS. It's shown in a JS syntax-highlighted codeblock for clarity.

```js
1; // (lambda: exec("print('Hello Python')", globals()))()
lambda: eval("console.log('Hello JS')");
```

- The first statement, ignoring the JS comment, is simply an integer. It does nothing.
- The second statement utilizes a clever trick with JS Labeled Statements: The `lambda: ` at the start is treated as a label and is ignored. The eval is executed like normal and delivers the execution of the JS code in a string.

This effectively only runs the JavaScript code.

### Summary

And just like that, we've managed to ignore the JS portion in Python and the Python portion in JS. Pretty neat!

While it seems simple in hindsight, this solution took a _long_ time to figure out (even though some aspects of it are hiding in plain sight), so I hope it's interesting!