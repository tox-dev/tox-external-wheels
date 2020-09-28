from setuptools import setup

setup(
    use_scm_version={"write_to": "src/tox_external_wheels/version.py"},
    install_requires=["tox>=3.12.2", "six<2.0.0"],
)
