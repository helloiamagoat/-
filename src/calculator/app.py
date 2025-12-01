"""Graphical calculator application built with Tkinter."""

from __future__ import annotations

import ast
import operator
import tkinter as tk
from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict, Union


Number = Union[int, float]


# Supported operations for safe evaluation
_ALLOWED_OPERATORS: Dict[type, Callable[[Number, Number], Number]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_ALLOWED_UNARY_OPERATORS: Dict[type, Callable[[Number], Number]] = {
    ast.UAdd: lambda a: a,
    ast.USub: operator.neg,
}


class EvaluationError(ValueError):
    """Raised when an expression cannot be evaluated safely."""


def _evaluate_ast(node: ast.AST) -> Number:
    if isinstance(node, ast.Expression):
        return _evaluate_ast(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise EvaluationError("Unsupported constant")

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPERATORS:
        operand = _evaluate_ast(node.operand)
        return _ALLOWED_UNARY_OPERATORS[type(node.op)](operand)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate_ast(node.left)
        right = _evaluate_ast(node.right)
        try:
            return _ALLOWED_OPERATORS[type(node.op)](left, right)
        except ZeroDivisionError as exc:  # pragma: no cover - runtime feedback
            raise EvaluationError("Division by zero") from exc

    raise EvaluationError("Unsupported expression")


def safe_eval(expression: str) -> Number:
    """Safely evaluate a math expression using the allowed operators."""

    try:
        parsed = ast.parse(expression, mode="eval")
        return _evaluate_ast(parsed)
    except (SyntaxError, EvaluationError) as exc:
        raise EvaluationError("Invalid expression") from exc


@dataclass
class CalculatorState:
    expression: str = ""
    result: str = "0"
    error: str = ""

    def append(self, value: str) -> None:
        self.expression += value

    def clear(self) -> None:
        self.expression = ""
        self.result = "0"
        self.error = ""

    def backspace(self) -> None:
        if self.expression:
            self.expression = self.expression[:-1]


class CalculatorApp:
    """A simple calculator with basic arithmetic operations."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Калькулятор")
        self.state = CalculatorState()
        self.display_var = tk.StringVar(value=self.state.result)
        self.history_var = tk.StringVar(value=self.state.expression)

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self) -> None:
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

    def _build_layout(self) -> None:
        history_label = tk.Label(
            self.root,
            textvariable=self.history_var,
            anchor="e",
            bg="#0d1117",
            fg="#8b949e",
            padx=10,
        )
        history_label.grid(row=0, column=0, columnspan=4, sticky="nsew")

        display = tk.Entry(
            self.root,
            textvariable=self.display_var,
            font=("SF Pro Display", 20),
            justify="right",
            bd=0,
            bg="#161b22",
            fg="#c9d1d9",
            readonlybackground="#161b22",
        )
        display.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=(0, 10))
        display.configure(state="readonly")

        buttons = [
            ("C", self.clear, 2, 0),
            ("⌫", self.backspace, 2, 1),
            ("%", partial(self.append, "%"), 2, 2),
            ("/", partial(self.append, "/"), 2, 3),
            ("7", partial(self.append, "7"), 3, 0),
            ("8", partial(self.append, "8"), 3, 1),
            ("9", partial(self.append, "9"), 3, 2),
            ("*", partial(self.append, "*"), 3, 3),
            ("4", partial(self.append, "4"), 4, 0),
            ("5", partial(self.append, "5"), 4, 1),
            ("6", partial(self.append, "6"), 4, 2),
            ("-", partial(self.append, "-"), 4, 3),
            ("1", partial(self.append, "1"), 5, 0),
            ("2", partial(self.append, "2"), 5, 1),
            ("3", partial(self.append, "3"), 5, 2),
            ("+", partial(self.append, "+"), 5, 3),
            ("0", partial(self.append, "0"), 6, 0),
            (".", partial(self.append, "."), 6, 1),
            ("=", self.calculate, 6, 2, 2),
        ]

        for label, command, row, col, colspan in [
            (*btn, 1) if len(btn) == 4 else btn for btn in buttons
        ]:
            self._create_button(label, command, row, col, colspan)

        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(2, 7):
            self.root.grid_rowconfigure(i, weight=1)

        self.root.bind("<Return>", lambda event: self.calculate())

    def _create_button(self, text: str, command: Callable[[], None], row: int, column: int, colspan: int) -> None:
        btn = tk.Button(
            self.root,
            text=text,
            command=command,
            bd=0,
            bg="#21262d",
            fg="#c9d1d9",
            activebackground="#30363d",
            activeforeground="#ffffff",
            font=("SF Pro Display", 14),
            padx=10,
            pady=12,
        )
        btn.grid(row=row, column=column, columnspan=colspan, sticky="nsew", padx=5, pady=5)

    def append(self, value: str) -> None:
        self.state.append(value)
        self.history_var.set(self.state.expression)

    def clear(self) -> None:
        self.state.clear()
        self.display_var.set(self.state.result)
        self.history_var.set("")

    def backspace(self) -> None:
        self.state.backspace()
        self.history_var.set(self.state.expression)

    def calculate(self) -> None:
        expression = self.state.expression or self.state.result
        try:
            result = safe_eval(expression)
        except EvaluationError:
            self.state.result = "Ошибка"
        else:
            self.state.result = str(result)
        self.display_var.set(self.state.result)
        self.history_var.set(expression)


def main() -> None:
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
