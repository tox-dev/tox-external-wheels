import os
import sys
from shutil import copy
from time import sleep

import pytest


def test_simple_config(initproj, cmd, whl_dir):
    """Test whether a simple external_wheel config works"""
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
    """Test whether a more complex external_wheel config works"""
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
    """Test whether a more complex external_wheel config works with different commands"""
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
    """Test whether finding newest wheel function works (in case where pattern matches more
    than 1 file"""
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


@pytest.mark.negative
def test_err_missing_wheel_config(initproj, cmd, whl_dir):
    """Tests whether a use friendly error is thrown when no wheel file can be found"""
    initproj(
        "cool_app-0.4.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            external_wheels =
                {toxinidir}/missing_app-1.0.0-py2.py3-none-any.whl
            commands=python -c "print('perform')"
        """
        },
    )
    result = cmd()
    result.assert_fail()
    assert "MissingWheelFile: No wheel file was found with pattern:" in result.err


@pytest.mark.skipif(sys.platform == "win32", reason="bash unavailable on Windows")
def test_external_build_config_unix(initproj, cmd, whl_dir):
    """Test that external build works on Unix"""
    test_dir = str(
        initproj(
            "cool_app-0.4.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                external_build =
                    chmod +x build.bash
                    ./build.bash
                external_wheels =
                    {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                commands=python -c "print('perform')"
            """,
                "build.bash": """#!/bin/bash
                mv super_app_asd-1.0.0-py2.py3-none-any.whl super_app-1.0.0-py2.py3-none-any.whl
            """,
            },
        )
    )
    copy(
        os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"),
        os.path.join(test_dir, "super_app_asd-1.0.0-py2.py3-none-any.whl"),
    )
    result = cmd()
    result.assert_success()


@pytest.mark.negative
@pytest.mark.skipif(sys.platform == "win32", reason="bash unavailable on Windows")
def test_external_build_err_unix(initproj, cmd, whl_dir):
    """Test whether non 0 exit code from external build is handled correctly"""
    initproj(
        "cool_app-0.4.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            external_build =
                chmod +x build.bash
                ./build.bash
            commands=python -c "print('perform')"
        """,
            "build.bash": """#!/bin/bash
            exit 1
        """,
        },
    )
    result = cmd()
    assert "ERROR" in result.out
    assert (
        "ExternalBuildNonZeroReturn: ExternalBuildNonZeroReturn: "
        "'./build.bash' exited with return code: 1" in result.err
    )
    assert result.ret == 1


@pytest.mark.skipif(sys.platform != "win32", reason="bash unavailable on Windows")
def test_external_build_config_win(initproj, cmd, whl_dir):
    """Test that external build works on Windows"""
    test_dir = str(
        initproj(
            "cool_app-0.4.0",
            filedefs={
                "tox.ini": """
                [tox]
                envlist = py
                [testenv]
                external_build =
                    move super_app_asd-1.0.0-py2.py3-none-any.whl super_app-1.0.0-py2.py3-none-any.whl
                external_wheels =
                    {toxinidir}/super_app-1.0.0-py2.py3-none-any.whl
                commands=python -c "print('perform')"
            """,
            },
        )
    )
    copy(
        os.path.join(whl_dir, "super_app-1.0.0-py2.py3-none-any.whl"),
        os.path.join(test_dir, "super_app_asd-1.0.0-py2.py3-none-any.whl"),
    )
    result = cmd()
    result.assert_success()


@pytest.mark.negative
@pytest.mark.skipif(sys.platform != "win32", reason="bash unavailable on Windows")
def test_external_build_err_win(initproj, cmd, whl_dir):
    """Test whether non 0 exit code from external build is handled correctly on Windows"""
    initproj(
        "cool_app-0.4.0",
        filedefs={
            "tox.ini": """
            [tox]
            envlist = py
            [testenv]
            external_build =
                EXIT /B 1
            commands=python -c "print('perform')"
        """,
        },
    )
    result = cmd()
    assert "ERROR" in result.out
    assert (
            "ExternalBuildNonZeroReturn: ExternalBuildNonZeroReturn: "
            "'./build.bash' exited with return code: 1" in result.err
    )
    assert result.ret == 1
