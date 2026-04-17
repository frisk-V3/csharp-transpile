#!/usr/bin/env python3
"""
CLI entrypoint for c2t (C# -> JS/Python transpiler).
Usage:
  c2t input.cs --out-dir out --emit js,py --emit-types none
"""
import argparse
import sys
import os
from .parser import parse_program
from .gen_js import JSGenerator
from .gen_py import PyGenerator

def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="c2t", description="C# subset -> JS/Python transpiler")
    p.add_argument("input", help="Input C# file")
    p.add_argument("--out-dir", "-o", default="dist", help="Output directory")
    p.add_argument("--emit", default="js,py", help="Comma separated targets: js,py")
    p.add_argument("--emit-types", default="none", choices=["none","pyhint","jsdoc"], help="Emit type hints")
    args = p.parse_args(argv)

    src = open(args.input, "r", encoding="utf-8").read()
    program = parse_program(src)

    emits = [e.strip() for e in args.emit.split(",") if e.strip()]
    if "js" in emits:
        gen = JSGenerator(emit_types=(args.emit_types=="jsdoc"))
        out = gen.generate(program)
        write_file(os.path.join(args.out_dir, "out.js"), out)
        print("Wrote", os.path.join(args.out_dir, "out.js"))
    if "py" in emits:
        gen = PyGenerator(emit_types=(args.emit_types=="pyhint"))
        out = gen.generate(program)
        write_file(os.path.join(args.out_dir, "out.py"), out)
        print("Wrote", os.path.join(args.out_dir, "out.py"))

if __name__ == "__main__":
    main()
