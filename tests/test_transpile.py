import tempfile
import os
from c2t.parser import parse_program
from c2t.gen_py import PyGenerator
from c2t.gen_js import JSGenerator

def test_basic_transpile():
    src = open(os.path.join(os.path.dirname(__file__),"../examples/hello.cs")).read()
    prog = parse_program(src)
    py = PyGenerator(emit_types=False).generate(prog)
    js = JSGenerator(emit_types=False).generate(prog)
    assert "def add" in py
    assert "function add" in js
