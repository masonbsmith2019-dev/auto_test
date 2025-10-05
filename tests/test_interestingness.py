from auto_test.ast_index import AstIndex
from auto_test.interestingness import compute_metrics


def test_recursive_interestingness_example():
    with open("examples/sample.py", "r", encoding="utf-8") as f:
        code = f.read()

    idx = AstIndex(code, debug=True)
    nested, interesting, calls = compute_metrics(idx, debug=True)

    # Validate nestedness counts for the constructed example
    assert nested["c"] == 2
    assert nested["b"] == 4
    assert nested["a"] == 5

    # Validate interestingness with recursive 0.5 depth multiplier
    # a: 5 + 0.5 * (b: 4 + 0.5 * (c: 2)) = 5 + 0.5 * (4 + 1) = 7.5
    assert interesting["c"] == 2.0
    assert interesting["b"] == 5.0
    assert interesting["a"] == 7.5


