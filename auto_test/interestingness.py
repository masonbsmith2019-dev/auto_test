# autotestsmith/metrics.py

def compute_metrics(ast_index, debug: bool = False):
    """Compute nestedness and recursively weighted interestingness.

    Interestingness for function f is:
      T(f) = nested(f) + 0.5 * sum_{c in calls(f)} T(c)

    This yields depth-weighting by powers of 0.5 across call chains.
    Cycles are handled conservatively by cutting recursion when a back-edge is encountered.
    """
    nested = {}
    calls = {}

    for name, node in ast_index.functions():
        nested[name] = ast_index.nestedness(node)
        calls[name] = ast_index.calls_in_func(node)

    # Memoized DFS to compute T(name) as defined above
    memo = {}
    visiting = set()

    def total_score(name):
        if name in memo:
            return memo[name]
        if name in visiting:
            # Cycle detected: only count own nestedness to avoid infinite recursion
            return nested[name]
        visiting.add(name)
        subtotal = 0.0
        if debug:
            print(f"\n--- compute: {name} ---")
            print(f"  nestedness={nested[name]}")
            print(f"  calls={calls.get(name, [])}")
        for callee in calls.get(name, []):
            if callee in nested:
                child = total_score(callee)
                if debug:
                    print(f"    ↳ {name} -> {callee}: contributes {child}")
                subtotal += child
        visiting.remove(name)
        score = nested[name] + 0.5 * subtotal
        memo[name] = score
        if debug:
            print(f"  subtotal(children)={subtotal}")
            print(f"  score={score}")
        return score

    if debug:
        print("\n=== Interestingness: per-function details ===")
    interesting = {name: total_score(name) for name in nested}
    if debug:
        print("\n=== Interestingness: summary ===")
        for name in nested:
            print(f"  {name}: nested={nested[name]} interesting={interesting[name]} calls={calls.get(name, [])}")

    return nested, interesting, calls


