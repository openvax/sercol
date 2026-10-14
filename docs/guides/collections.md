# Select, order and track values

## Remove duplicates and sort

```python
from sercol import Collection

values = Collection([5, 2, 3, 2], distinct=True, sort_key=abs)
print(list(values))
```

```text
[2, 3, 5]
```

`distinct=True` uses a set, so elements must be hashable and their input order
is not retained. Supply `sort_key` when you need a predictable order.

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

`sources` labels where values came from; it does not open those files.
`source` requires exactly one source. `filenames` strips directory components.

## Extend the collection

A subclass should accept the state passed by `clone_with_new_elements()`:
`elements`, `distinct`, `sort_key` and `sources`, or override that cloning
operation. Implement its own `to_dict()` with constructor-compatible keys to
support serialization. `Collection.to_dict()` deliberately rejects subclasses
that have not supplied their own implementation.
