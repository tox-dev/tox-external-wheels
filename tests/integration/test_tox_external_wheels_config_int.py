import os
from shutil import copy
from time import sleep


def test_simple_config(initproj, cmd, whl_dir):
    test_dir = str(
        initproj(
            "cool_app-0.4.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                external_wheels =
                    {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                commands=python -c "print('perform')"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    result = cmd()
    result.assert_success()


def test_more_complex_config(initproj, cmd, whl_dir):
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                external_wheels =
                    a: {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                    b: {toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl
                commands=python -c "print('perform')"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd()
    assert "super" in result.session.venv_dict["py-a"].package
    assert "subpar" in result.session.venv_dict["py-b"].package
    result.assert_success()


def test_different_commands(initproj, cmd, whl_dir):
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                external_wheels =
                    a: {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                    b: {toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl
                commands =
                    a: python -c "import super_app"
                    b: python -c "import subpar_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd()
    assert "super" in result.session.venv_dict["py-a"].package
    assert "subpar" in result.session.venv_dict["py-b"].package
    result.assert_success()


def test_finding_newest_whl(initproj, cmd, whl_dir):
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                external_wheels =
                    {toxinidir}/*app*.whl
                commands =
                    python -c "import subpar_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    sleep(1)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd()
    assert "subpar" in result.session.venv_dict["py"].package
    result.assert_success()


def test_finding_partial_ext_wheel(initproj, cmd, whl_dir):
    """Test whether fallback to regular source installation works"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                external_wheels =
                    a: {toxinidir}/*app*.whl
                commands =
                    a: python -c "import subpar_app"
                    b: python -c "import alright_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd()
    assert "subpar" in result.session.venv_dict["py-a"].package
    assert str(result.session.venv_dict["py-b"].package).endswith("alright_app-0.2.0.zip")
    result.assert_success()


def test_invalid_whl(initproj, cmd):
    str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                external_wheels =
                    *app*.whl
                commands =
                    python -c "print('done')"
            """
            },
        )
    )
    result = cmd()
    assert result.ret == 1
    assert "No wheel file was found with pattern: " in result.out
