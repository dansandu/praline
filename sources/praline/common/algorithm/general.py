from functools import reduce


def cartesian_product(superset):
    result = []
    count = reduce(lambda x, y: x * len(y), superset, 1) if superset else 0
    for i in range(0, count):
        divisor = 1
        element = []
        for subset in superset:
            element.append(subset[(i // divisor) % len(subset)])
            divisor *= len(subset)
        result.append(element)
    return result
