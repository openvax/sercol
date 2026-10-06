# sercol

Filter and group a collection while keeping its collection type and source
metadata. `Collection` is also the base class used by several OpenVax libraries
for variants, effects and predictions.

## Install

```sh
python -m pip install sercol
```

Python 3.9 or later is required.

## Filter and group values

```python
from sercol import Collection

values = Collection([5, 2, 3, 2])
selected = values.filter(lambda value: value >= 3)
groups = values.groupby(lambda value: value % 2)
print(list(selected))
print({key: list(group) for key, group in groups.items()})
```

```text
[5, 3]
{1: [5, 3], 0: [2, 2]}
```

`filter()` returns a collection; `groupby()` returns a dictionary of
collections. Both preserve the original collection class and constructor state.
The original collection is unchanged.

## Save and reload

Continuing with `values` above:

```python
restored = Collection.from_json(values.to_json())
print(list(restored))
print(restored == values)
```

```text
[5, 2, 3, 2]
True
```

Serialization uses [serializable](https://github.com/openvax/serializable).
Elements and constructor state must be supported by that format; callable
sorting keys need to be importable when reconstructing the collection.

See [select, order and track values](guides/collections.md) for thresholds,
multiple grouping keys and source metadata. The [API reference](reference.md)
lists all collection operations.
