import os
import sys
from shutil import copy
from time import sleep

import pytest


def test_simple_param(initproj, cmd, whl_dir):
    """Test whether a simple external_wheel config works"""
    test_dir = str(
        initproj(
            "cool_app-0.4.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                commands=python -c "print('perform')"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    result = cmd("--external_wheels", "{toxinidir}/super_app-1.0.0-py2.py3-none-any.whl")
    result.assert_success()


def test_more_complex_config(initproj, cmd, whl_dir):
    """Test whether a more comlicated external_wheel config works"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                commands=python -c "print('perform')"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd(
        "--external_wheels",
        "a:{toxinidir}/super_app-1.0.0-py2.py3-none-any.whl;"
        "b:{toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl",
    )
    assert "super" in result.session.venv_dict["py-a"].package
    assert "subpar" in result.session.venv_dict["py-b"].package
    result.assert_success()


def test_different_commands(initproj, cmd, whl_dir):
    """Test whether a more complex external_wheel config works with different commands"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                commands =
                    a: python -c "import super_app"
                    b: python -c "import subpar_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd(
        "--external_wheels",
        "a:{toxinidir}/super_app-1.0.0-py2.py3-none-any.whl;"
        "b:{toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl",
    )
    assert "super" in result.session.venv_dict["py-a"].package
    assert "subpar" in result.session.venv_dict["py-b"].package
    result.assert_success()


def test_finding_newest_whl(initproj, cmd, whl_dir):
    """Test whether finding newest wheel function works (in case where pattern
    matches more than 1 file"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                commands =
                    python -c "import subpar_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    sleep(1)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd("--external_wheels", "{toxinidir}/*app*.whl")
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
                commands =
                    a: python -c "import subpar_app"
                    b: python -c "import alright_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd("--external_wheels", "a: {toxinidir}/*app*.whl")
    assert "subpar" in result.session.venv_dict["py-a"].package
    assert str(result.session.venv_dict["py-b"].package).endswith("alright_app-0.2.0.zip")
    result.assert_success()


def test_param_override(initproj, cmd, whl_dir):
    """Make sure parameter overrides config value"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                external_wheels =
                    a: {toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl
                    b: {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                commands =
                    a: python -c "import super_app"
                    b: python -c "import subpar_app"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd(
        "--external_wheels",
        "a:{toxinidir}/super_app-1.0.0-py2.py3-none-any.whl;"
        "b:{toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl",
    )
    assert "super" in result.session.venv_dict["py-a"].package
    assert "subpar" in result.session.venv_dict["py-b"].package
    result.assert_success()


@pytest.mark.negative
def test_err_invalid_whl(initproj, cmd):
    """Test whether user friendly error is thrown if no wheel file is found"""
    initproj(
        "alright_app-0.2.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            commands =
                python -c "print('done')"
        """
        },
    )
    result = cmd("--external_wheels", "*app*.whl")
    assert result.ret == 1
    assert "MissingWheelFile: No wheel file was found with pattern: " in result.err


@pytest.mark.negative
@pytest.mark.parametrize("env", ["py", "py-a", "py-b"])
def test_err_pattern_clashing(initproj, cmd, whl_dir, env):
    """Test whether a user friendly error is thrown when parameter external
    wheel environments clash"""
    test_dir = str(
        initproj(
            "alright_app-0.2.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py-{a,b}
                [testenv]
                external_wheels =
                    a: {toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl
                    b: {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                commands =
                    python -c "exit(1)"
            """
            },
        )
    )
    copy(os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"), test_dir)
    copy(os.path.join(whl_dir, "subpar_app-0.2.0-py2.py3-none-any.whl"), test_dir)
    result = cmd(
        "--external_wheels",
        "{}: {{toxinidir}}/non_existent_app-0.0.1-py2.py3-none-any.whl;".format(env)
        + "a:{toxinidir}/super_app-1.0.0-py2.py3-none-any.whl;"
        + "b:{toxinidir}/subpar_app-0.2.0-py2.py3-none-any.whl",
    )
    assert result.ret == 1
    assert (
        "These patterns: ['" in result.err
        and "'] all match the current environment '" in result.err
    )


@pytest.mark.skipif(sys.platform == "win32", "bash unavailable on Windows")
def test_external_build_param(initproj, cmd, whl_dir):
    """Test whether simple external build works in parameter form"""
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
            """,
                "build.bash": """#!/bin/bash
                pwd
                mv super_app_asd-1.0.0-py2.py3-none-any.whl super_app-1.0.0-py2.py3-none-any.whl
            """,
            },
        )
    )
    copy(
        os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"),
        os.path.join(test_dir, "super_app_asd-1.0.0-py2.py3-none-any.whl"),
    )
    result = cmd("--external_build", "chmod +x build.bash; ./build.bash")
    result.assert_success()


@pytest.mark.negative
def test_external_build_missing_param(cmd):
    """Test whether external build cannot be called without a value"""
    result = cmd("--external_build")
    assert result.ret == 2
    assert "tox: error: argument --external_build: expected one argument" in result.err


@pytest.mark.negative
@pytest.mark.skipif(sys.platform == "win32", "bash unavailable on Windows")
def test_external_build_err(initproj, cmd, whl_dir):
    """Test whether non 0 exit code from external build is handled correctly"""
    initproj(
        "cool_app-0.4.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            commands=python -c "print('perform')"
        """,
            "build.bash": """#!/bin/bash
            exit 1
        """,
        },
    )
    result = cmd("--external_build", "chmod +x build.bash; ./build.bash")
    assert "ERROR" in result.out
    assert (
        "ExternalBuildNonZeroReturn: ExternalBuildNonZeroReturn: "
        "'chmod +x build.bash; ./build.bash' exited with return code: 1" in result.err
    )
    assert result.ret == 1


@pytest.mark.skipif(sys.platform == "win32", "bash unavailable on Windows")
def test_external_build_param_overwrite(initproj, cmd, whl_dir):
    """Test whether external build parameter overwrites config external build"""
    initproj(
        "cool_app-0.4.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            external_build=
               chmod +x bad_build.bash
               bad_build.bash
            commands=python -c "print('perform')"
        """,
            "build.bash": """#!/bin/bash
            exit 0
        """,
            "bad_build.bash": """#!/bin/bash
            exit 1""",
        },
    )
    result = cmd("--external_build", "chmod +x build.bash; ./build.bash")
    result.assert_success()
