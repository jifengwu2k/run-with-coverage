import subprocess
import os
import os.path
import sys
from typing import Optional, Sequence


def run_with_coverage(script: str, args: Sequence[str], coverage_file: str) -> bool:
    """
    Runs a Python script with coverage tracking.

    Args:
        script: The path to the Python script to run.
        args:  A sequence of arguments to pass to the script.
        coverage_file: The path to the coverage data file.

    Returns:
        True if the coverage file was created/updated successfully, False otherwise.
    """

    script = os.path.abspath(script)

    coverage_file = os.path.abspath(coverage_file)

    # Use a list to build the command for clarity
    command = ['coverage', 'run', '--append', script] + list(args)

    # Coverage collects execution data in a file called `.coverage`
    # If need be, you can set a new file name with the COVERAGE_FILE environment variable.
    env = os.environ.copy()
    env['COVERAGE_FILE'] = coverage_file

    try:
        proc = subprocess.Popen(
            command,
            env=env
        )
        proc.wait()  # Wait for the process to complete

        return os.path.isfile(coverage_file)

    except FileNotFoundError:
        print("Error: `coverage` command not found.  Make sure `coverage` is installed and in your PATH.", file=sys.stderr)
        return False
    except Exception as e:  # Catch other potential errors during subprocess execution
        print(f"An error occurred: {e}", file=sys.stderr)
        return False