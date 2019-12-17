def test_version():
    pkg = __import__("tox_external_wheels", fromlist=["__version__"])
    assert pkg.__version__
