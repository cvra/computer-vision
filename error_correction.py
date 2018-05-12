from functools import reduce
from itertools import permutations

VALID_SEQUENCES = [
    ['Orange',  'Black',  'Green'],
    ['Yellow',  'Black',   'Blue'],
    [  'Blue',  'Green', 'Orange'],
    ['Yellow',  'Green',  'Black'],
    [ 'Black', 'Yellow', 'Orange'],
    [ 'Green', 'Yellow',   'Blue'],
    [  'Blue', 'Orange',  'Black'],
    [ 'Green', 'Orange', 'Yellow'],
    [ 'Black',   'Blue',  'Green'],
    ['Orange',   'Blue', 'Yellow'],
]

def color_diff_weight(x):
    if x[0] == x[1]:
        return 0.0

    elif set(['None', 'Yellow']).issubset(set(x)):
        return 0.5

    elif set(['None', 'Orange']).issubset(set(x)):
        return 0.5

    elif set(['Orange', 'Yellow']).issubset(set(x)):
        return 0.8

    elif 'Black' in set(x):
        return 0.9

    elif 'None' in set(x):
        return 0.9

    else:
        return 1.0

def _distance(colorA, colorB):
    pairwise_distances = map(lambda x: color_diff_weight(x), zip(colorA, colorB))
    return reduce(lambda x, y: x + y, pairwise_distances)

def distance(colorA, colorB):
    distance_forward = _distance(colorA, colorB)
    distance_reverse = _distance(colorA, reversed(colorB))
    return min(distance_forward, distance_reverse)

def _argmin(array):
    min_value = min(array)
    min_indices = []
    for i, value in enumerate(array):
        if value <= min_value:
            min_indices.append(i)
    return min_indices

def adjust(colors):
    if colors:
        if len(colors) == 3:
            yield colors

        elif len(colors) == 2:
            for pos in range(3):
                new_sequ = colors.copy()
                new_sequ.insert(pos, 'None')
                yield new_sequ
    else:
        yield


def error_correction(colors):
    adjusted_color = adjust(colors)

    min_dist = 3
    best_fit = None

    for input_sequ in adjusted_color:
        distances = [distance(input_sequ, sequence) for sequence in VALID_SEQUENCES]
        best_fits = [VALID_SEQUENCES[i] for i in _argmin(distances)]

        if min(distances) < min_dist:
            min_dist = min(distances)
            best_fit = [VALID_SEQUENCES[i] for i in _argmin(distances)][0]

    return best_fit, min_dist