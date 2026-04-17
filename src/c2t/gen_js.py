from .ir import *
from .util import indent
from typing import Optional

class JSGenerator:
    def __init__(self, emit_types: bool=False):
        self.emit_types = emit_types

    def generate(self, program: Program) -> str:
        parts = []
        for cls in program.classes:
            for m in cls.methods:
                parts.append(self.gen_method(m))
        return "\n\n".join(parts) + "\n"

    def gen_method(self, m: MethodDef) -> str:
        params = ", ".join(name for name, _ in m.params)
        header = f"function {m.name}({params}) {{"
        body = self.gen_block(m.body)
        return header + "\n" + indent("\n".join(body), 4) + "\n}"

    def gen_block(self, stmts):
        lines = []
        for s in stmts:
            lines.extend(self.gen_stmt(s))
        return lines

    def gen_stmt(self, s):
        if isinstance(s, VarDecl):
            init = ""
            if s.init:
                init = " = " + self.gen_expr(s.init)
            if self.emit_types and s.var_type:
                # emit as comment above
                return [f"// {s.var_type}", f"let {s.name}{init};"]
            return [f"let {s.name}{init};"]
        if isinstance(s, Assign):
            return [f"{s.target} = {self.gen_expr(s.expr)};"]
        if isinstance(s, ExprStmt):
            return [self.gen_expr(s.expr) + ";"]
        if isinstance(s, Return):
            if s.expr:
                return [f"return {self.gen_expr(s.expr)};"]
            return ["return;"]
        if isinstance(s, If):
            cond = self.gen_expr(s.cond)
            then_block = "\n".join(self.gen_block(s.then_body))
            out = [f"if ({cond}) {{", indent("\n".join(self.gen_block(s.then_body)),4), "}"]
            if s.else_body:
                out.append("else {")
                out.append(indent("\n".join(self.gen_block(s.else_body)),4))
                out.append("}")
            return out
        if isinstance(s, While):
            return ["while (" + self.gen_expr(s.cond) + ") {", indent("\n".join(self.gen_block(s.body)),4), "}"]
        raise NotImplementedError(type(s))

    def gen_expr(self, e):
        if isinstance(e, Literal):
            if isinstance(e.value, str):
                return '"' + e.value.replace('"','\\"') + '"'
            if isinstance(e.value, bool):
                return "true" if e.value else "false"
            return str(e.value)
        if isinstance(e, VarRef):
            return e.name
        if isinstance(e, BinaryOp):
            return f"({self.gen_expr(e.left)} {e.op} {self.gen_expr(e.right)})"
        if isinstance(e, UnaryOp):
            return f"({e.op}{self.gen_expr(e.operand)})"
        raise NotImplementedError(type(e))
