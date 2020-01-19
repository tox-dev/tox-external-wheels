import glob
import os
from subprocess import STDOUT, Popen

import pluggy
from tox import reporter

from .exception import ExternalBuildNonZeroReturn, MissingWheelFile, MultipleMatchingPatterns

hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    """Add a command line option for later use"""
    parser.add_testenv_attribute(
        name="external_wheels",
        type="string",
        default=None,
        help="locations of external wheel files",
    )
    parser.add_testenv_attribute(
        name="external_build",
        type="string",
        default=None,
        help="location of an external build script",
    )
    parser.add_argument(
        "--external_wheels",
        action="store",
        help="semi-colon separated list of external wheel paths",
    )
    parser.add_argument("--external_build", action="store", help="external wheel build script")


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
            raise MultipleMatchingPatterns(
                "These patterns: {} all match the current environment '{}'".format(
                    matching_patterns, venv.name
                )
            )
    elif venv.envconfig.external_wheels:
        pattern = venv.envconfig.external_wheels
    if pattern:
        # If a pattern is NOT found we fall off and return None, this will cause fallback
        # to source installation
        files = [os.path.expanduser(os.path.expandvars(f)) for f in glob.glob(pattern)]
        if not files:
            raise MissingWheelFile("No wheel file was found with pattern: '{}'".format(pattern))
        if len(files) > 1:
            # Choose the file with the newest modification date
            files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return files[0]


@hookimpl
def tox_configure(config):
    def run_system_cmd(cmd):
        """Helper to report running command and also to actually run the command"""
        reporter.line("external_build: running command: {}".format(cmd))
        p_cmd = Popen(cmd, shell=True, stderr=STDOUT)
        stdout, _ = p_cmd.communicate()
        if p_cmd.returncode != 0:
            reporter.error("external_build: stdout+stderr: {}".format(p_cmd.returncode, stdout))
            raise ExternalBuildNonZeroReturn(
                "'{}' exited with return code: {}".format(cmd, p_cmd.returncode)
            )

    try:
        param_index = config.args.index("--external_build")
        run_system_cmd(config.args[param_index + 1])
    except ValueError:
        for env in config.envlist:
            for cmd in config.envconfigs[env]._reader.getlist("external_build"):
                run_system_cmd(cmd)
