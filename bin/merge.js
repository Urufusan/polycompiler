#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const zlib = require('zlib');
const { promisify } = require('util');

const compress = promisify(zlib.deflate);

async function main() {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.error(`Usage: ${path.basename(process.argv[1])} <file1> <file2> [output-file]`);
        console.error("Compression can also be utilized with the following example:");
        console.error(`${path.basename(process.argv[1])} merge.js merge.py merge.py.js -C`);
        process.exit(1);
    }

    const useCompression = args.includes("-C");
    if (useCompression) {
        args.splice(args.indexOf("-C"), 1);
    }

    const file1Path = args[0];
    const file2Path = args[1];
    const outputPath = args[2] || 'out/result.py.js';

    // Check if files exist
    try {
        await fs.access(file1Path);
        await fs.access(file2Path);
    } catch (err) {
        console.error(`Error: One or more input files do not exist.`);
        process.exit(1);
    }

    // Get file extensions
    const ext1 = path.extname(file1Path).toLowerCase();
    const ext2 = path.extname(file2Path).toLowerCase();

    // Check if one is Python and one is JavaScript
    const isPython = ext => ['.py'].includes(ext);
    const isJavaScript = ext => ['.js', '.cjs', '.mjs'].includes(ext);

    const hasPython = isPython(ext1) || isPython(ext2);
    const hasJS = isJavaScript(ext1) || isJavaScript(ext2);

    if (!(hasPython && hasJS)) {
        console.error(`Merging ${ext1.slice(1)} and ${ext2.slice(1)} is not supported. Only Python and JavaScript files can be merged.`);
        process.exit(1);
    }

    // Read file contents
    const content1 = await fs.readFile(file1Path, 'utf8');
    const content2 = await fs.readFile(file2Path, 'utf8');

    // Determine which file is Python and which is JavaScript
    const pythonContent = isPython(ext1) ? content1 : content2;
    const jsContent = isJavaScript(ext1) ? content1 : content2;

    // Call the merge function
    const merged = await mergeFiles(pythonContent, jsContent, useCompression);

    // Ensure the output directory exists
    const outputDir = path.dirname(outputPath);
    await fs.mkdir(outputDir, { recursive: true });

    // Write the result to the output file
    await fs.writeFile(outputPath, merged);
    console.log(`Merged files written to ${outputPath}`);
}

/**
 * Merges Python and JavaScript files
 * @param {string} pythonContent - Content of the Python file
 * @param {string} jsContent - Content of the JavaScript file
 * @param {boolean} compression - Whether to use compression
 * @returns {string} - Merged content
 */
async function mergeFiles(pythonContent, jsContent, compression = false) {
    let pyBuffer = Buffer.from(pythonContent, 'utf8');
    let jsBuffer = Buffer.from(jsContent, 'utf8');

    if (compression) {
        pyBuffer = await compress(pyBuffer, { level: zlib.constants.Z_BEST_COMPRESSION });
        jsBuffer = await compress(jsBuffer, { level: zlib.constants.Z_BEST_COMPRESSION });
    }

    const base64PythonContent = pyBuffer.toString('base64');
    const base64JsContent = jsBuffer.toString('base64');

    if (compression) {
        return `eval(["exec(__import__('zlib').decompress(__import__('base64').b64decode('${base64PythonContent}')).decode(encoding='utf-8',errors='ignore'))","(async () => eval(await new Response((await new Blob([Uint8Array.from(atob('${base64JsContent}'),c=>c.charCodeAt())]).stream().pipeThrough(new DecompressionStream('deflate')))).text()))()"][1|0==2]);`;
    } else {
        return `eval(["exec(__import__('base64').b64decode('${base64PythonContent}').decode(encoding='utf-8',errors='ignore'))","eval(atob('${base64JsContent}'))"][1|0==2]);`;
    }
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});