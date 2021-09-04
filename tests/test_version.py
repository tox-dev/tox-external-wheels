def test_version() -> None:
    from tox_external_wheels import __version__

    assert __version__
