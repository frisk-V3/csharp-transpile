"""
A tiny hand-written parser for a small C# subset.
Supported:
 - class X { static return_type name(params) { ... } }
 - int/string/bool literals
 - var declarations: int x = 1;
 - assignments: x = expr;
 - if, while, return
 - binary ops + - * / == != < > <= >=
This is intentionally minimal to be practical for a first transpiler.
"""
import re
from .ir import *
from typing import List, Tuple, Optional

TOKEN_SPEC = [
    ("NUMBER",   r"\d+"),
    ("STRING",   r"\"(\\.|[^\"])*\""),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"==|!=|<=|>=|[+\-*/<>=]"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("LBRACE",   r"\{"),
    ("RBRACE",   r"\}"),
    ("SEMI",     r";"),
    ("COMMA",    r","),
    ("WS",       r"[ \t\r\n]+"),
    ("OTHER",    r"."),
]

MASTER = re.compile("|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPEC))

class Token:
    def __init__(self, typ, val):
        self.type = typ
        self.val = val
    def __repr__(self):
        return f"Token({self.type},{self.val})"

def tokenize(src: str):
    for m in MASTER.finditer(src):
        typ = m.lastgroup
        val = m.group(typ)
        if typ == "WS":
            continue
        yield Token(typ, val)

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else Token("EOF","")

    def next(self):
        t = self.peek()
        self.i += 1
        return t

    def expect(self, typ, val=None):
        t = self.next()
        if t.type != typ or (val is not None and t.val != val):
            raise SyntaxError(f"Expected {typ} {val}, got {t.type} {t.val}")
        return t

    def parse_program(self) -> Program:
        classes = []
        while self.peek().type != "EOF":
            classes.append(self.parse_class())
        return Program(classes)

    def parse_class(self) -> ClassDef:
        # accept optional 'public' or 'private' or nothing
        if self.peek().type == "ID" and self.peek().val in ("public","private","internal","sealed","static"):
            self.next()
        self.expect("ID", "class")
        name = self.expect("ID").val
        self.expect("LBRACE")
        methods = []
        while self.peek().type != "RBRACE":
            methods.append(self.parse_method())
        self.expect("RBRACE")
        return ClassDef(name, methods)

    def parse_method(self) -> MethodDef:
        # accept optional modifiers
        is_static = False
        while self.peek().type == "ID" and self.peek().val in ("public","private","static"):
            tok = self.next()
            if tok.val == "static":
                is_static = True
        # return type
        ret_type = None
        if self.peek().type == "ID":
            ret_type = self.next().val
        name = self.expect("ID").val
        self.expect("LPAREN")
        params = []
        if self.peek().type != "RPAREN":
            while True:
                ptype = self.expect("ID").val
                pname = self.expect("ID").val
                params.append((pname, ptype))
                if self.peek().type == "COMMA":
                    self.next()
                    continue
                break
        self.expect("RPAREN")
        self.expect("LBRACE")
        body = self.parse_block()
        self.expect("RBRACE")
        return MethodDef(name=name, params=params, body=body, return_type=ret_type, is_static=is_static)

    def parse_block(self) -> List[Stmt]:
        stmts = []
        while self.peek().type not in ("RBRACE","EOF"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self) -> Stmt:
        t = self.peek()
        if t.type == "ID" and t.val in ("int","string","bool"):
            return self.parse_vardecl()
        if t.type == "ID" and t.val == "if":
            return self.parse_if()
        if t.type == "ID" and t.val == "while":
            return self.parse_while()
        if t.type == "ID" and t.val == "return":
            self.next()
            if self.peek().type == "SEMI":
                self.next()
                return Return(None)
            expr = self.parse_expr()
            self.expect("SEMI")
            return Return(expr)
        # assignment or expression stmt
        if t.type == "ID":
            # lookahead for assignment
            if self.tokens[self.i+1].type == "OP" and self.tokens[self.i+1].val == "=":
                name = self.next().val
                self.expect("OP","=")
                expr = self.parse_expr()
                self.expect("SEMI")
                return Assign(name, expr)
        # expression statement
        expr = self.parse_expr()
        self.expect("SEMI")
        return ExprStmt(expr)

    def parse_vardecl(self) -> VarDecl:
        vtype = self.next().val
        name = self.expect("ID").val
        init = None
        if self.peek().type == "OP" and self.peek().val == "=":
            self.next()
            init = self.parse_expr()
        self.expect("SEMI")
        return VarDecl(name=name, var_type=vtype, init=init)

    def parse_if(self) -> If:
        self.expect("ID","if")
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        self.expect("LBRACE")
        then_body = self.parse_block()
        self.expect("RBRACE")
        else_body = None
        if self.peek().type == "ID" and self.peek().val == "else":
            self.next()
            self.expect("LBRACE")
            else_body = self.parse_block()
            self.expect("RBRACE")
        return If(cond, then_body, else_body)

    def parse_while(self) -> While:
        self.expect("ID","while")
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        self.expect("LBRACE")
        body = self.parse_block()
        self.expect("RBRACE")
        return While(cond, body)

    # Expression parsing: precedence climbing
    PRECEDENCE = {
        "==": 5, "!=":5, "<":5, ">":5, "<=":5, ">=":5,
        "+":10, "-":10,
        "*":20, "/":20,
    }

    def parse_expr(self, min_prec=0):
        t = self.peek()
        if t.type == "NUMBER":
            self.next()
            left = Literal(int(t.val), typ="int")
        elif t.type == "STRING":
            self.next()
            val = t.val[1:-1].encode("utf-8").decode("unicode_escape")
            left = Literal(val, typ="string")
        elif t.type == "ID":
            self.next()
            if t.val in ("true","false"):
                left = Literal(True if t.val=="true" else False, typ="bool")
            else:
                left = VarRef(t.val)
        elif t.type == "LPAREN":
            self.next()
            left = self.parse_expr()
            self.expect("RPAREN")
        elif t.type == "OP" and t.val in ("-","!"):
            op = self.next().val
            operand = self.parse_expr(100)
            left = UnaryOp(op, operand)
        else:
            raise SyntaxError(f"Unexpected token in expression: {t}")

        while True:
            nxt = self.peek()
            if nxt.type == "OP" and nxt.val in self.PRECEDENCE and self.PRECEDENCE[nxt.val] >= min_prec:
                op = self.next().val
                prec = self.PRECEDENCE[op]
                # right-assoc not needed
                right = self.parse_expr(prec+1)
                left = BinaryOp(left, op, right)
                continue
            break
        return left

def parse_program(src: str) -> Program:
    tokens = tokenize(src)
    p = Parser(tokens)
    return p.parse_program()
