[![Tests](https://github.com/openvax/sercol/actions/workflows/tests.yml/badge.svg)](https://github.com/openvax/sercol/actions/workflows/tests.yml)
<a href="https://coveralls.io/github/openvax/sercol?branch=master">
    <img src="https://coveralls.io/repos/openvax/sercol/badge.svg?branch=master&service=github" alt="Coverage Status" />
</a>
<a href="https://pypi.python.org/pypi/sercol/">
    <img src="https://img.shields.io/pypi/v/sercol.svg?maxAge=1000" alt="PyPI" />
</a>

# sercol

Filter and group a collection while keeping its collection type and source
metadata. `Collection` is the base class for `varcode.VariantCollection`,
`varcode.EffectCollection` and `mhctools.BindingPredictionCollection`.

## Install and filter

```sh
python -m pip install sercol
```

Python 3.9 or later is required.

```python
from sercol import Collection

values = Collection([5, 2, 3, 2])
print(list(values.filter(lambda value: value >= 3)))
# [5, 3]
```

## Documentation

- [Group values, save and reload](docs/index.md)
- [Select, order and track values](docs/guides/collections.md)
- [API reference](docs/reference.md)

To build the documentation locally, run
`python -m pip install -r requirements-docs.txt` and `./docs.sh`.
