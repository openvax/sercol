[![Tests](https://github.com/openvax/sercol/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/openvax/sercol/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/openvax/sercol/badge.svg?branch=master&service=github)](https://coveralls.io/github/openvax/sercol?branch=master)
[![Documentation](https://github.com/openvax/sercol/actions/workflows/documentation.yml/badge.svg?branch=master)](https://openvax.github.io/sercol/)
[![PyPI](https://img.shields.io/pypi/v/sercol.svg)](https://pypi.org/project/sercol/)

# sercol

sercol provides `Collection`, a sequence that filters and groups while keeping
its collection type and source metadata, and saves to JSON through
[serializable](https://github.com/openvax/serializable). It is the base class
for [varcode](https://github.com/openvax/varcode)'s `VariantCollection` and
`EffectCollection` and [mhctools](https://github.com/openvax/mhctools)'
`BindingPredictionCollection`, so their filtering and grouping behave the same.

## Install

```sh
python -m pip install sercol
```

sercol needs Python 3.11 or later; it installs serializable and pandas.

## Quick start

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

`filter()` returns a new collection and `groupby()` a dictionary of
collections, each of the original class with the same constructor state. The
original collection is unchanged.

## Documentation

The [documentation](https://openvax.github.io/sercol/) covers, in reading order:

1. [Getting started](https://openvax.github.io/sercol/): filter, group, save
   and reload.
2. [Select, order and track values](https://openvax.github.io/sercol/guides/collections/):
   duplicates, sorting, threshold lookups, multiple groups, source metadata
   and subclassing.
3. [API reference](https://openvax.github.io/sercol/reference/).

## Development

```sh
python -m pip install -e . pytest pytest-cov ruff
./lint.sh   # ruff check
./test.sh   # pytest with coverage
python -m pip install -r requirements-docs.txt
./docs.sh   # mkdocs build --strict, then a rendered-link check
python scripts/check_docs_examples.py   # run docs examples, compare output
```

## License

Apache 2.0; see [LICENSE](https://github.com/openvax/sercol/blob/master/LICENSE).
