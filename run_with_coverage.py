# encoding: utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
import argparse
import logging
import shutil
import sys
import tempfile

from ctypes_unicode_proclaunch import launch, wait
from posix_or_nt import posix_or_nt
from read_unicode_environment_variables_dictionary import read_unicode_environment_variables_dictionary
from textcompat import filesystem_str_to_text, text_to_filesystem_str
from typing import Sequence, Text

if posix_or_nt() == 'nt':
    import ntpath as os_path

    # Explicitly specify a pure ASCII the Windows temp directory
    TEMP_DIR = 'C:\\Windows\\Temp'
else:
    import posixpath as os_path

    # Automatically pick a temp directory on POSIX
    TEMP_DIR = None


def run_with_coverage(absolute_script_path, args, absolute_coverage_path, measure_library_code=False):
    # type: (Text, Sequence[Text], Text, bool) -> None
    """
    Runs a Python script with coverage tracking.
    """
    logging.debug('Preparing to run script with coverage.')
    logging.debug('Script path: %s', absolute_script_path)
    logging.debug('Arguments: %s', args)
    logging.debug('Coverage output path: %s', absolute_coverage_path)

    executable = filesystem_str_to_text(sys.executable)
    if not executable:
        raise RuntimeError('Cannot retrieve the absolute path of the executable binary for the Python interpreter.')

    # Use a list to build the command for clarity
    arguments = [executable, u'-m', u'coverage', u'run']
    if measure_library_code:
        arguments.extend((u'--include', u'*'))
    arguments.append(absolute_script_path)
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
        environment = read_unicode_environment_variables_dictionary()
        environment[u'COVERAGE_FILE'] = filesystem_str_to_text(temp_file_name)

        logging.debug('Launching process:')
        exit_code = wait(launch(arguments, environment=environment))
        logging.info('Process exited with code: %s', exit_code)
    except Exception as e:
        logging.error('Error while running process: %s', e)
        raise
    finally:
        if os_path.exists(temp_file_name):
            logging.debug('Moving temp coverage file to final destination: %s', absolute_coverage_path)
            shutil.move(temp_file_name, text_to_filesystem_str(absolute_coverage_path))
            return exit_code


def configure_logging(verbose=False):
    # type: (bool) -> None
    log_level = logging.DEBUG if verbose else logging.INFO
    root_logger = logging.getLogger()

    # Prevent adding duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(handler)

    root_logger.setLevel(log_level)


def main():
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

    main_parser.add_argument(
        '-L', '--measure-library-code',
        action='store_true',
        help='Measure library code'
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
    coverage_file = filesystem_str_to_text(os_path.abspath(main_args.coverage))
    verbose = main_args.verbose
    measure_library_code = main_args.measure_library_code

    configure_logging(verbose)

    # Parse sub args
    sub_args = sub_parser.parse_args(sub_argv)
    script = filesystem_str_to_text(os_path.abspath(sub_args.script))
    script_args = list(map(filesystem_str_to_text, sub_args.script_args))

    sys.exit(run_with_coverage(script, script_args, coverage_file, measure_library_code))


if __name__ == '__main__':
    main()
