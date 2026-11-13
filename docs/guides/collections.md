# Select, order and track values

This guide covers the `Collection` options beyond plain filtering and
grouping: removing duplicates, sorting, selecting by looked-up values,
putting one element in several groups, recording sources, and writing a
subclass.

## Remove duplicates and sort

```python
from sercol import Collection

values = Collection([5, 2, 3, 2], distinct=True, sort_key=abs)
print(list(values))
```

```text
[2, 3, 5]
```

`distinct=True` keeps the first occurrence of each element, in input order, so
elements must be hashable. `sort_key` then sorts what remains; elements with
equal keys keep their input order.

## Select by a value lookup

```python
scores = {"alpha": 2.0, "beta": 0.5}
names = Collection(["alpha", "beta", "unknown"])
selected = names.filter_above_threshold(
    key_fn=lambda name: name,
    value_dict=scores,
    threshold=1.0,
)
print(list(selected))
```

```text
['alpha']
```

The comparison is strictly greater than the threshold. Missing keys receive
`default_value`, which defaults to zero. Use `filter_any_above_threshold()`
when each element supplies several lookup keys and any one may qualify.

## Put an element in several groups

```python
words = Collection(["ab", "bc"])
groups = words.multi_groupby(lambda word: set(word))
print({key: list(groups[key]) for key in sorted(groups)})
```

```text
{'a': ['ab'], 'b': ['ab', 'bc'], 'c': ['bc']}
```

`multi_groupby()` accepts an iterable of keys for each element. Return distinct
keys for each element when it should appear only once in each group.

## Keep source metadata

```python
values = Collection([1, 2, 3], sources={"results.csv"})
selected = values.filter(lambda value: value > 1)
print(selected.source)
print(selected.filenames)
```

```text
results.csv
['results.csv']
```

`sources` labels where values came from; it does not open those files. Each
collection keeps its own copy of the set, so adding a source to one collection
doesn't change another. `source` requires exactly one source. `filenames`
strips directory components and is sorted; `filename` is its first entry, and
raises `ValueError` when there is none.

Two collections are equal when they have the same class, the same elements in
the same order and the same sources:

```python
print(values == Collection([1, 2, 3], sources={"results.csv"}))
print(values == Collection([1, 2, 3], sources={"other.csv"}))
```

```text
True
False
```

## Extend the collection

`filter()` and the grouping methods build their results with
`clone_with_new_elements()`, which passes `elements`, `distinct`, `sort_key`
and `sources` to the subclass constructor. A constructor may leave out any of
`distinct`, `sort_key` and `sources`, and may give its first argument another
name:

```python
class Scores(Collection):
    def __init__(self, scores, sources=None):
        Collection.__init__(self, scores, sort_key=abs, sources=sources)

scores = Scores([-3, 1, 2], sources={"results.csv"})
high = scores.filter(lambda score: abs(score) > 1)
print(type(high).__name__, list(high), high.source)
```

```text
Scores [2, -3] results.csv
```

A constructor with other required arguments must override
`clone_with_new_elements()`; otherwise cloning raises a `TypeError` which says
so.

A subclass whose constructor takes exactly `elements`, `distinct`, `sort_key`
and `sources`, for example one that inherits `Collection.__init__`, can be
pickled, copied and saved as JSON as it is. A subclass whose constructor takes other arguments
must implement its own `to_dict()` returning them; `Collection.to_dict()`
raises `ValueError` for it rather than return state its constructor cannot
accept.
