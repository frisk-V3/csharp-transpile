# IR node definitions for a small C# subset
from typing import List, Optional, Tuple, Any

class Node:
    pass

class Program(Node):
    def __init__(self, classes: List["ClassDef"]):
        self.classes = classes

class ClassDef(Node):
    def __init__(self, name: str, methods: List["MethodDef"]):
        self.name = name
        self.methods = methods

class MethodDef(Node):
    def __init__(self, name: str, params: List[Tuple[str,str]], body: List["Stmt"], return_type: Optional[str]=None, is_static: bool=True):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
        self.is_static = is_static

# Statements
class Stmt(Node):
    pass

class VarDecl(Stmt):
    def __init__(self, name: str, var_type: Optional[str]=None, init: Optional["Expr"]=None):
        self.name = name
        self.var_type = var_type
        self.init = init

class Assign(Stmt):
    def __init__(self, target: str, expr: "Expr"):
        self.target = target
        self.expr = expr

class If(Stmt):
    def __init__(self, cond: "Expr", then_body: List[Stmt], else_body: Optional[List[Stmt]]=None):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body

class While(Stmt):
    def __init__(self, cond: "Expr", body: List[Stmt]):
        self.cond = cond
        self.body = body

class Return(Stmt):
    def __init__(self, expr: Optional["Expr"]):
        self.expr = expr

class ExprStmt(Stmt):
    def __init__(self, expr: "Expr"):
        self.expr = expr

# Expressions
class Expr(Node):
    pass

class Literal(Expr):
    def __init__(self, value: Any, typ: Optional[str]=None):
        self.value = value
        self.typ = typ

class VarRef(Expr):
    def __init__(self, name: str):
        self.name = name

class BinaryOp(Expr):
    def __init__(self, left: Expr, op: str, right: Expr):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Expr):
    def __init__(self, op: str, operand: Expr):
        self.op = op
        self.operand = operand

# Utility
def flatten_block(stmts):
    out = []
    for s in stmts:
        out.append(s)
    return out
