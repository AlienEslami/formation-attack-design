"""Independent checks of the new budget formulas; proofs remain in main.tex."""
from itertools import permutations, product
from pathlib import Path
import json

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'verification_output'


def grounded_matrix(count, edges):
    incidence = np.zeros((len(edges), count - 1), dtype=int)
    for row, (source, receiver) in enumerate(edges):
        if source:
            incidence[row, source - 1] = -1
        incidence[row, receiver - 1] = 1
    return incidence.T @ incidence


def exact_sigma(matrix):
    return [1 / matrix[i:, i:].inv()[0, 0] for i in range(matrix.rows)]


def degree_bound(sigma, budget):
    return min(max(s / d**2 for s, d in zip(sigma, degrees))
               for degrees in product(*(range(1, i + 2) for i in range(len(sigma))))
               if sum(degrees) <= budget)


def verify():
    complete = []
    for count in range(2, 9):
        matrix = count * sp.eye(count - 1) - sp.ones(count - 1)
        sigma = exact_sigma(matrix)
        assert sigma == [sp.Rational(count * i, i + 1) for i in range(1, count)]
        for budget in range(count - 1, 2 * count - 2):
            remaining = 2 * (count - 1) - budget
            bound = degree_bound(sigma, budget)
            assert bound == sp.Rational(count * remaining, remaining + 1)
            complete.append({'N': count, 'links': budget, 'normalized_bound': str(bound)})

    matrix = sp.Matrix([[3, 0, -1, -1], [0, 3, -1, -1],
                        [-1, -1, 3, 0], [-1, -1, 0, 3]])
    follower_edges = [(0, 2), (0, 3), (1, 2), (1, 3)]
    sparse_orders = []
    for order in permutations(range(4)):
        if any(order.index(j) >= order.index(i) for j, i in follower_edges):
            continue
        sigma = exact_sigma(matrix.extract(order, order))
        assert sigma == [sp.Rational(15, 7), sp.Rational(7, 3), 3, 3]
        assert degree_bound(sigma, 6) == sp.Rational(7, 3)
        assert degree_bound(sigma, 7) == sp.Rational(15, 7)
        sparse_orders.append([i + 1 for i in order])
    assert len(sparse_orders) == 4
    harmonic = matrix.inv()[:, 0] / matrix.inv()[0, 0]
    assert harmonic == sp.Matrix([1, sp.Rational(2, 7), sp.Rational(3, 7), sp.Rational(3, 7)])
    follower_weights = sp.zeros(4)
    for i in range(1, 4):
        follower_weights[i, 0] = harmonic[i]
    response = (sp.eye(4) - follower_weights).inv()
    alpha = [1] + [max(harmonic[i], 1 - harmonic[i]) for i in range(1, 4)]
    gains = [alpha[i]**2 * (response[:, i].T * matrix * response[:, i])[0]
             for i in range(4)]
    assert max(gains) == sp.Rational(15, 7)

    tree_count = 0
    for count in range(2, 8):
        for parents in product(*(range(i) for i in range(1, count))):
            edges = [(parent, i) for i, parent in enumerate(parents, 1)]
            matrix_array = grounded_matrix(count, edges)
            weights = np.zeros((count - 1, count - 1), dtype=int)
            for parent, i in edges:
                if parent:
                    weights[i - 1, parent - 1] = 1
            response_array = np.eye(count - 1, dtype=int)
            power = np.eye(count - 1, dtype=int)
            for _ in range(count - 2):
                power = power @ weights
                response_array += power
            assert np.all(np.diag(response_array.T @ matrix_array @ response_array) == 1)
            inverse = np.linalg.inv(matrix_array)
            for parent, i in edges:
                if parent == 0:
                    assert np.isclose(inverse[i - 1, i - 1], 1)
            tree_count += 1

    random_checks = 0
    rng = np.random.default_rng(20261109)
    max_violation = 0.0
    for count in range(2, 11):
        for _ in range(40):
            edges = {(int(rng.integers(i)), i) for i in range(1, count)}
            edges.update((j, i) for i in range(1, count) for j in range(i)
                         if rng.random() < .35)
            matrix_array = grounded_matrix(count, sorted(edges))
            weights = np.zeros((count, count))
            degrees = []
            for i in range(1, count):
                selected = rng.choice(i, size=int(rng.integers(1, i + 1)), replace=False)
                values = rng.uniform(.05, 1, len(selected))
                weights[i, selected] = values / values.sum()
                degrees.append(len(selected))
            response_array = np.linalg.inv(np.eye(count - 1) - weights[1:, 1:])
            energies = np.diag(response_array.T @ matrix_array @ response_array)
            gain = np.max(weights[1:].max(axis=1)**2 * energies)
            sigma_array = np.array([1 / np.linalg.inv(matrix_array[i:, i:])[0, 0]
                                    for i in range(count - 1)])
            bound = np.max(sigma_array / np.array(degrees)**2)
            max_violation = max(max_violation, bound - gain)
            assert bound <= gain + 1e-10
            random_checks += 1

    report = {
        'passed': True,
        'complete_graph_exact_budget_checks': complete,
        'sparse_admissible_orders': sparse_orders,
        'sparse_six_link_normalized_lower_bound': '7/3',
        'sparse_seven_link_normalized_optimum': '15/7',
        'outward_tree_designs_checked': tree_count,
        'random_graph_and_weight_checks': random_checks,
        'largest_floating_point_bound_violation': max_violation,
        'scope': 'Exact algebraic examples and sampled implementation checks supplement the proofs in the manuscript.'
    }
    OUT.mkdir(exist_ok=True)
    (OUT / 'budget_checks.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    result = verify()
    print(json.dumps({key: value for key, value in result.items()
                      if key != 'complete_graph_exact_budget_checks'}, indent=2))
