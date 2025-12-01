import pytest

from calculator.app import CalculatorState, EvaluationError, safe_eval


def test_safe_eval_basic_operations():
    assert safe_eval("1+2*3") == 7
    assert safe_eval("(4-1)/3") == 1
    assert safe_eval("2**3") == 8
    assert safe_eval("10%3") == 1


def test_safe_eval_unary_operations():
    assert safe_eval("-5 + 2") == -3
    assert safe_eval("+4") == 4


def test_safe_eval_division_by_zero():
    with pytest.raises(EvaluationError):
        safe_eval("1/0")


def test_safe_eval_invalid_expressions():
    with pytest.raises(EvaluationError):
        safe_eval("2 +")
    with pytest.raises(EvaluationError):
        safe_eval("abs(-1)")
    with pytest.raises(EvaluationError):
        safe_eval("'oops'")


def test_calculator_state_flow():
    state = CalculatorState()
    state.append("1")
    state.append("+")
    state.append("2")
    assert state.expression == "1+2"

    state.backspace()
    assert state.expression == "1+"

    state.clear()
    assert state.expression == ""
    assert state.result == "0"
    assert state.error == ""
