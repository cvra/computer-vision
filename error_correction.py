from functools import reduce

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

def _distance(colorA, colorB):
    pairwise_distances = map(lambda x: 0 if x[0] == x[1] else 1, zip(colorA, colorB))
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

def error_correction(colors):
    distances = [distance(colors, sequence) for sequence in VALID_SEQUENCES]
    best_fits = [VALID_SEQUENCES[i] for i in _argmin(distances)]
    return best_fits, min(distances)

assert 0 == _distance(['Orange', 'Blue'], ['Orange',   'Blue'])
assert 1 == _distance(['Orange', 'Blue'], [ 'Black',   'Blue'])
assert 2 == _distance(['Orange', 'Blue'], [  'Blue', 'Orange'])

assert 0 == distance(['Orange', 'Black', 'Green'], ['Orange', 'Black',  'Green'])
assert 0 == distance(['Orange', 'Black', 'Green'], [ 'Green', 'Black', 'Orange'])
assert 1 == distance(['Orange', 'Black', 'Green'], [ 'Black', 'Black', 'Orange'])
assert 1 == distance(['Orange', 'Black', 'Green'], ['Orange', 'Black',  'Black'])
assert 2 == distance(['Orange', 'Black', 'Green'], ['Orange',  'Blue',  'Black'])

assert [0] == _argmin([1,2,3])
assert [2] == _argmin([3,2,1,2,3])
assert [2,3,4] == _argmin([3,2,1,1,1,2,3])

assert ['Orange', 'Black', 'Green'] == error_correction(['Orange', 'Black',  'Green'])[0][0]
assert ['Orange', 'Black', 'Green'] == error_correction([ 'Green', 'Black', 'Orange'])[0][0]
assert ['Orange', 'Black', 'Green'] == error_correction([  'Grey', 'Black', 'Orange'])[0][0]
assert ['Orange', 'Black', 'Green'] == error_correction([  'Grey', 'White', 'Orange'])[0][0]
assert ['Orange', 'Black', 'Green'] == error_correction(['Orange', 'Black', 'Yellow'])[0][0]
assert ['Orange', 'Black', 'Green'] == error_correction(['Orange',  'Blue',  'Green'])[0][0]
assert [ 'Black',  'Blue', 'Green'] == error_correction(['Orange',  'Blue',  'Green'])[0][1]
assert ['Orange', 'Blue', 'Yellow'] == error_correction(['Orange',  'Blue',  'Green'])[0][2]
