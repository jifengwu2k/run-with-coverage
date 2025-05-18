# Run With Coverage

Run a Python script with coverage tracking and allow the user to specify the coverage data file.

## Prerequisites

*   Python 3.6 or newer
*   `coverage` Python package.  Install with:

    ```bash
    pip install coverage
    ```

## Usage

```python
from run_with_coverage import run_with_coverage

script_to_run = "my_script.py"  # Replace with your script
args = ["--verbose", "some_argument"]  # Optional arguments
coverage_file = "/path/to/coverage.dat"  # Optional coverage file

success = run_with_coverage(script_to_run, args, coverage_file)

if success:
    print(f"Coverage run completed successfully. Results saved to {coverage_file}")
else:
    print("Coverage run failed.")
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
