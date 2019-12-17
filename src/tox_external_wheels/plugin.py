import glob
import os

import pluggy
from tox import reporter

hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    """Add a command line option for later use"""
    parser.add_testenv_attribute(
        name="external_wheel",
        type="string",
        default=None,
        help="an argument pulled from the tox.ini",
    )


@hookimpl
def tox_package(session, venv):
    if venv.envconfig.external_wheel:
        pattern = venv.envconfig.external_wheel
        files = [os.path.expanduser(os.path.expandvars(f)) for f in glob.glob(pattern)]
        if not files:
            reporter.error("No wheel file was found with pattern: {}".format(pattern))
            SystemExit(1)
        if len(files) > 1:
            # Choose the file with the newest modification date
            files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return files[0]
