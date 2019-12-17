import os

import pytest

pytest_plugins = "tox._pytestplugin"


@pytest.fixture(scope="session")
def whl_dir():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "wheels/")
