# encoding: utf-8
from __future__ import print_function

import argparse
import logging
import os
import os.path
import shutil
import sys
import tempfile

from posix_or_nt import posix_or_nt
from strcompat import filesystem_string_to_unicode, unicode_to_filesystem_string

IS_NT = posix_or_nt() == 'nt'
if IS_NT:
    from proclaunch.nt import Process, get_env_dict

    # Explicitly specify a pure ASCII the Windows temp directory
    TEMP_DIR = 'C:\\Windows\\Temp'
else:
    from proclaunch.posix import Process, get_env_dict

    # Automatically pick a temp directory on Posix
    TEMP_DIR = None


def run_with_coverage(absolute_script_path, args, absolute_coverage_path):
    """
    Runs a Python script with coverage tracking.

    Args:
        absolute_script_path (unicode): The absolute path to the Python script to run.
        args (Sequence[unicode]):  A sequence of arguments to pass to the script.
        absolute_coverage_path (unicode): The absolute path to the coverage data file.
    """
    logging.debug('Preparing to run script with coverage.')
    logging.debug('Script path: %s', absolute_script_path)
    logging.debug('Arguments: %s', args)
    logging.debug('Coverage output path: %s', absolute_coverage_path)

    executable = filesystem_string_to_unicode(sys.executable)
    if not executable:
        raise RuntimeError('Cannot retrieve the absolute path of the executable binary for the Python interpreter.')

    # Use a list to build the command for clarity
    arguments = [executable, u'-m', u'coverage', u'run', absolute_script_path]
    arguments.extend(args)

    # Coverage collects execution data in a file called `.coverage`
    # If need be, you can set a new file name with the COVERAGE_FILE environment variable.

    # `int sqlite3_open(const char *filename, sqlite3 **ppDb);`
    # SQLite requires the `filename` parameter to be UTF-8 encoded, even on Windows.
    # Since Windows uses 'mbcs' encoding for environment variables, this can lead to
    # subtle issues if the path contains non-ASCII characters.
    # To avoid problems when coverage (which uses SQLite) writes its data file,
    # we create a temporary file with an ASCII-only path.
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
    temp_file_name = temp_file.name
    temp_file.close()

    logging.debug('Temporary file for coverage created at: %s', temp_file_name)
    exit_code = None
    try:
        env_dict = get_env_dict()
        env_dict[u'COVERAGE_FILE'] = filesystem_string_to_unicode(temp_file_name)

        logging.debug('Launching process:')

        proc = Process.from_arguments(arguments, env_dict=env_dict)
        proc.run()
        exit_code = proc.wait()

        logging.info('Script exited with code: %s', exit_code)
    except Exception as e:
        logging.error('Error while running script: %s', e)
        raise
    finally:
        if os.path.exists(temp_file_name):
            logging.debug('Moving temp coverage file to final destination: %s', absolute_coverage_path)
            shutil.move(temp_file_name, unicode_to_filesystem_string(absolute_coverage_path))
            return exit_code


def configure_logging(verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO
    root_logger = logging.getLogger()

    # Prevent adding duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(handler)

    root_logger.setLevel(log_level)


if __name__ == '__main__':
    description = 'Run a Python script with coverage tracking'
    usage = '%(prog)s [OPTIONS] -- SCRIPT [SCRIPT_ARGS...]'

    # Main parser for args before `--`
    main_parser = argparse.ArgumentParser(
        description=description,
        usage=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    main_parser.add_argument(
        '-c', '--coverage',
        default='.coverage',
        help='Coverage data file (default: %(default)s)'
    )

    main_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )

    # Sub parser for args after `--`
    sub_parser = argparse.ArgumentParser(
        add_help=False,
        description=description,
        usage=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    sub_parser.add_argument(
        'script',
        help='Script to run'
    )

    sub_parser.add_argument(
        'script_args',
        nargs=argparse.REMAINDER,
        help='Arguments for the script'
    )

    # Find index of dash
    try:
        dash_index = sys.argv.index('--')
        main_argv = sys.argv[1:dash_index]
        sub_argv = sys.argv[dash_index + 1:]
    except ValueError:
        main_argv = sys.argv[1:]
        sub_argv = []

    # Parse main args
    main_args = main_parser.parse_args(main_argv)
    coverage_file = filesystem_string_to_unicode(os.path.abspath(main_args.coverage))
    verbose = main_args.verbose

    configure_logging(verbose)

    # Parse sub args
    sub_args = sub_parser.parse_args(sub_argv)
    script = filesystem_string_to_unicode(os.path.abspath(sub_args.script))
    script_args = list(map(filesystem_string_to_unicode, sub_args.script_args))

    sys.exit(run_with_coverage(script, script_args, coverage_file))
