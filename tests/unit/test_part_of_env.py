import pytest

from tox_external_wheels.plugin import part_of_env


@pytest.mark.parametrize(
    "pattern,env",
    [
        ("a", "py-a"),
        ("py-a", "py-a"),
        ("py-mark", "py-b-something-mark"),
        ("mark", "py-b-something-mark"),
        ("something", "py-b-something-mark"),
        ("b", "py-b-something-mark"),
        ("!amanda", "py-b-something-mark"),
        ("py-!amanda", "py-b-something-mark"),
    ],
)
def test_combinations_positive(pattern, env):
    assert part_of_env(pattern, env)


@pytest.mark.parametrize(
    "pattern,env",
    [
        ("b", "py-a"),
        ("py-b", "py-a"),
        ("py-!mark", "py-b-something-mark"),
        ("mark", "py-b-something-amanda"),
        ("!something", "py-b-something-mark"),
        ("!py-!b-!something-!mark", "py-b-something-mark"),
    ],
)
def test_combinations_negative(pattern, env):
    assert not part_of_env(pattern, env)
