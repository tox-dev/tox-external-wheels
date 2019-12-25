[![Latest version on PyPi](https://badge.fury.io/py/tox-external-wheels.svg)](https://badge.fury.io/py/tox-external-wheels)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/tox-external-wheels.svg)](https://pypi.org/project/tox-external-wheels/)
[![Build Status](https://dev.azure.com/markoookeller/tox-external-wheels/_apis/build/status/keller00.tox-external-wheels?branchName=master)](https://dev.azure.com/markoookeller/tox-external-wheels/_build/latest?definitionId=2&branchName=master)
[![Documentation status](https://readthedocs.org/projects/tox-external-wheels/badge/?version=latest&style=flat-square)](https://tox-external-wheels.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# tox-external-wheels

Use externally created wheels with Tox

Features
--------

* The ability to define external wheel files to tests in the tox config (example tox file):

```
[tox]
envlist = py-{a,b,c}
[testenv]
external_wheels =
    a: {toxinidir}/dist/*py27*.whl
    b: {toxinidir}/dist/*py37*.whl
commands =
    a,b: pytest test
    c: pip list
```

Or defined in a command line argument

```
tox -e 'py-{a,b,c}' --external_wheels 'a:{toxinidir}/dist/*py27*.whl;b:{toxinidir}/dist/*py37*.whl'
```

**Note**: In this case `py-c` falls back to installing from source.


Requirements
------------

* None


Installation
------------

You can install "tox-external-wheels" via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org):

```
pip install tox-external-wheels
```

Usage
-----

Use the `external_wheel` option. Like shown in [usage](#usage)

Contributing
------------
Contributions are very welcome. Tests can be run with [tox](https://tox.readthedocs.io/en/latest/), please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the **MIT** license, `tox-external-wheels` is
free and open source software.


Issues
------

If you encounter any problems, please
[file an issue](https://github.com/keller00/tox-external-wheels/issues)
along with a detailed description.
