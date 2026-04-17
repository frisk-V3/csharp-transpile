from .ir import *
from .util import indent
from typing import Optional

class PyGenerator:
    def __init__(self, emit_types: bool=False):
        self.emit_types = emit_types

    def generate(self, program: Program) -> str:
        parts = []
        for cls in program.classes:
            for m in cls.methods:
                parts.append(self.gen_method(m))
        return "\n\n".join(parts) + "\n"

    def gen_method(self, m: MethodDef) -> str:
        params = ", ".join(name + (": " + typ if self.emit_types and typ else "") for name, typ in m.params)
        ret = (" -> " + m.return_type) if (self.emit_types and m.return_type) else ""
        header = f"def {m.name}({params}){ret}:"
        body_lines = self.gen_block(m.body)
        if not body_lines:
            body_lines = ["pass"]
        return header + "\n" + indent("\n".join(body_lines), 4)

    def gen_block(self, stmts):
        lines = []
        for s in stmts:
            lines.extend(self.gen_stmt(s))
        return lines

    def gen_stmt(self, s):
        if isinstance(s, VarDecl):
            if s.init:
                return [f"{s.name} = {self.gen_expr(s.init)}"]
            else:
                return [f"{s.name} = None"]
        if isinstance(s, Assign):
            return [f"{s.target} = {self.gen_expr(s.expr)}"]
        if isinstance(s, ExprStmt):
            return [self.gen_expr(s.expr)]
        if isinstance(s, Return):
            if s.expr:
                return [f"return {self.gen_expr(s.expr)}"]
            return ["return"]
        if isinstance(s, If):
            cond = self.gen_expr(s.cond)
            then = "\n".join(self.gen_block(s.then_body))
            out = [f"if {cond}:", indent(then,4)]
            if s.else_body:
                out.append("else:")
                out.append(indent("\n".join(self.gen_block(s.else_body)),4))
            return out
        if isinstance(s, While):
            return [f"while {self.gen_expr(s.cond)}:", indent("\n".join(self.gen_block(s.body)),4)]
        raise NotImplementedError(type(s))

    def gen_expr(self, e):
        if isinstance(e, Literal):
            if isinstance(e.value, str):
                return repr(e.value)
            if isinstance(e.value, bool):
                return "True" if e.value else "False"
            return str(e.value)
        if isinstance(e, VarRef):
            return e.name
        if isinstance(e, BinaryOp):
            return f"({self.gen_expr(e.left)} {e.op} {self.gen_expr(e.right)})"
        if isinstance(e, UnaryOp):
            return f"({e.op}{self.gen_expr(e.operand)})"
        raise NotImplementedError(type(e))
