[![Latest version on PyPi](https://badge.fury.io/py/tox-external-wheels.svg)](https://badge.fury.io/py/tox-external-wheels)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/tox-external-wheels.svg)](https://pypi.org/project/tox-external-wheels/)
[![Build Status](https://dev.azure.com/markoookeller/tox-external-wheels/_apis/build/status/keller00.tox-external-wheels?branchName=master)](https://dev.azure.com/markoookeller/tox-external-wheels/_build/latest?definitionId=2&branchName=master)
[![Documentation status](https://readthedocs.org/projects/tox-external-wheels/badge/?version=latest&style=flat-square)](https://tox-external-wheels.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/tox-external-wheels)](https://pepy.tech/project/tox-external-wheels)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# tox-external-wheels

Use externally created wheels with Tox

Features
--------

* The ability to define external wheel files to tests in the tox config (example `tox.ini` file):
```ini
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

```shell script
tox -e 'py-{a,b,c}' --external_wheels 'a:dist/*py27*.whl;b:dist/*py37*.whl'
```

**Notes**: In this case `py-c` falls back to installing from source. `tox-external_wheels` now supports ! in env names

* The ability to define an external command to build wheel(s) with (example `tox.ini` file):
```ini
[tox]
envlist = py-{a,b,c}
[testenv]
external_build=
    ./prepare_build.sh
    ./build.sh
external_wheels =
    {toxinidir}/dist/*.whl
commands =
    a,b: pytest test
    c: pip list
```

Or defined in a command line argument
```shell script
tox -e 'py-{a,b,c}' --external_build './build.sh'
```

**Note**: if command exits with non-zero return code, error will be reported and exception will be raised.

* Support installing dependencies from external wheel files by adding their name into the `external_wheels` in config

```ini
[tox]
envlist = py-{a,b,c}
[testenv]
deps = six
external_wheels =
    a: {toxinidir}/dist/*py27*.whl (six: six-*.whl[optional_extra])
    b: {toxinidir}/dist/*py37*.whl
commands =
    a,b: pytest test
    c: pip list
```

Or defined in a command line argument

```shell script
tox -e 'py-{a,b,c}' --external_wheels 'a:dist/*py27*.whl (six: six-*.whl[optional_extra]);b:/dist/*py37*.whl'
```


Requirements
------------

* tox


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
