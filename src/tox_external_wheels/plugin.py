import glob
import os

import pluggy
from tox import reporter

hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    """Add a command line option for later use"""
    parser.add_testenv_attribute(
        name="external_wheels",
        type="string",
        default=None,
        help="an argument pulled from the tox.ini",
    )
    parser.add_argument(
        "--external_wheels",
        action="store",
        help="Semi-colon separated list of external wheel paths",
    )


@hookimpl
def tox_package(session, venv):
    pattern = None
    # Argument overrides config
    if session.config.option.external_wheels:
        external_wheels = [
            e.split(":") if (":" in e) else ("", e)
            for e in session.config.option.external_wheels.split(";")
        ]
        matching_patterns = [
            venv.envconfig.setenv.reader._replace(v.strip())
            for k, v in external_wheels
            if k in venv.name
        ]
        if len(matching_patterns) == 1:
            pattern = matching_patterns[0]
        elif len(matching_patterns) > 1:
            reporter.error("More than one pattern matches current ".format(pattern))
            SystemExit(1)
    elif venv.envconfig.external_wheels:
        pattern = venv.envconfig.external_wheels
    if pattern:
        files = [os.path.expanduser(os.path.expandvars(f)) for f in glob.glob(pattern)]
        if not files:
            reporter.error("No wheel file was found with pattern: {}".format(pattern))
            SystemExit(1)
        if len(files) > 1:
            # Choose the file with the newest modification date
            files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return files[0]
