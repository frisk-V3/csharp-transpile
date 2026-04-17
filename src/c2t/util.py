# small helpers
def indent(lines, n=4):
    pad = " " * n
    return "\n".join(pad + line if line else "" for line in lines.splitlines())
