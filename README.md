[![Tests](https://github.com/openvax/sercol/actions/workflows/tests.yml/badge.svg)](https://github.com/openvax/sercol/actions/workflows/tests.yml)
<a href="https://coveralls.io/github/openvax/sercol?branch=master">
    <img src="https://coveralls.io/repos/openvax/sercol/badge.svg?branch=master&service=github" alt="Coverage Status" />
</a>
<a href="https://pypi.python.org/pypi/sercol/">
    <img src="https://img.shields.io/pypi/v/sercol.svg?maxAge=1000" alt="PyPI" />
</a>

# sercol

Rich collection class with grouping and filtering helpers. Used as a base class
for `varcode.EffectCollection`, `varcode.VariantCollection`, and `mhctools.EpitopeCollection`.

## Install and filter

```sh
python -m pip install sercol
```

```python
from sercol import Collection

values = Collection([5, 2, 3, 2])
print(list(values.filter(lambda value: value >= 3)))
# [5, 3]
```

[Home and grouping example](docs/index.md) · [Common tasks](docs/guides/collections.md) · [API reference](docs/reference.md)

Build the site with `python -m pip install -r requirements-docs.txt` and `./docs.sh`.
