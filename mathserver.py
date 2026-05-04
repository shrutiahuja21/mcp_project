import ast
import operator
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mathserver")

_BINOPS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
}


def _eval_arith(node: ast.AST) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return int(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_arith(node.operand)
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        fn = _BINOPS[type(node.op)]
        return int(fn(_eval_arith(node.left), _eval_arith(node.right)))
    msg = "only integer literals with +, -, *, parentheses, and unary minus"
    raise ValueError(msg)


@mcp.tool()
def evaluate(expression: str) -> int:
    """Evaluate one integer arithmetic expression, e.g. '(3+5)*12'. Use this for multi-step math."""
    if len(expression) > 256:
        raise ValueError("expression too long")
    tree = ast.parse(expression.strip(), mode="eval")
    return _eval_arith(tree.body)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")
   