"""Scientific calculator with a safe expression evaluator."""

import argparse
import ast
import math
from typing import Any, Callable


ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

ALLOWED_FUNCTIONS: dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "fabs": math.fabs,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
    "deg": math.degrees,
    "rad": math.radians,
}


class SafeEvaluator(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            return self._apply_binop(node.op, left, right)
        if isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            return self._apply_unaryop(node.op, operand)
        if isinstance(node, ast.Call):
            return self._apply_call(node)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            return self._lookup_name(node.id)
        raise ValueError(f"Unsupported expression: {ast.dump(node, include_attributes=False)}")

    def _apply_binop(self, op: ast.operator, left: float, right: float) -> float:
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left**right
        raise ValueError(f"Unsupported operator: {op}")

    def _apply_unaryop(self, op: ast.unaryop, operand: float) -> float:
        if isinstance(op, ast.UAdd):
            return +operand
        if isinstance(op, ast.USub):
            return -operand
        raise ValueError(f"Unsupported unary operator: {op}")

    def _apply_call(self, node: ast.Call) -> float:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed")
        func_name = node.func.id
        func = ALLOWED_FUNCTIONS.get(func_name)
        if func is None:
            raise ValueError(f"Unknown function '{func_name}'")
        args = [self.visit(arg) for arg in node.args]
        if node.keywords:
            raise ValueError("Keyword arguments are not supported")
        return func(*args)

    def _lookup_name(self, name: str) -> float:
        if name in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[name]
        raise ValueError(f"Unknown constant '{name}'")


def evaluate_expression(expression: str) -> float:
    parsed = ast.parse(expression, mode="eval")
    evaluator = SafeEvaluator()
    return evaluator.visit(parsed)


def run_repl() -> None:
    print("Scientific Calculator (type 'quit' to exit)")
    while True:
        try:
            expression = input("calc> ").strip()
        except EOFError:
            print()
            return
        if not expression:
            continue
        if expression.lower() in {"quit", "exit"}:
            return
        try:
            result = evaluate_expression(expression)
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}")
            continue
        print(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scientific calculator")
    parser.add_argument(
        "expression",
        nargs="?",
        help="Expression to evaluate (e.g. 'sin(pi/2) + log(10, 10)')",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.expression:
        result = evaluate_expression(args.expression)
        print(result)
    else:
        run_repl()


if __name__ == "__main__":
    main()
