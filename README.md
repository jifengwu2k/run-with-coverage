# Run With Coverage

Run a Python script with coverage tracking, allowing the user to specify the coverage data file - even in complex or non-standard environments.

- ✅ **Python 2 & 3 compatible**
- ✅ **Windows & POSIX support**
- ✅ **Unicode-safe**, including non-ASCII paths
- ✅ **Safe `.coverage` writing**, even when filenames contain spaces or non-UTF-8 characters
- ✅ **Temp file management compatible with SQLite's UTF-8-only file requirements**

> Fun Fact: The basic Unix implementation took 1 day. Windows compatibility (including the `posix-or-nt`, `proclaunch`, `strcompat` libraries) took 14. You're welcome.

## Why This Exists

Most test runners (`pytest`, `nose`, etc.) and coverage tools (`coverage.py`) make assumptions:

- Filenames are UTF-8 or ASCII
- Paths don't contain spaces or non-English characters
- Python 3 is the only target platform
- subprocess is sufficient for launching scripts

These assumptions **break** in:
- Internationalized environments (e.g. Chinese, Japanese, Cyrillic filenames)
- Enterprise and legacy systems still running **Python 2**
- **Windows**, where environment variables use `mbcs` and temp file encoding matters

## Usage

```bash
python -m run_with_coverage [-c <coverage_file>] [-v] -- <script_to_run> [args...]
```

- `-c`: Coverage output file (default: `.coverage`)
- `-v`: Enable verbose logging
- `--`: Required delimiter to separate runner options from the script being tested

## Example: Running on Windows with Non-ASCII Paths

This example runs a Python script in a Unicode path with arguments, saving the coverage file to a Unicode path as well.

Example script under test `C:\Users\Administrator\Desktop\路径 有空格\名字 有空格.py`:

```python
# coding=utf-8
from __future__ import print_function
import sys

for i, arg in enumerate(sys.argv):
    print('sys.argv[%d]=%s' % (i, arg))
```

Example command:

```
C:\Users\jifengwu2k\packages\run-with-coverage>python -m run_with_coverage -c "..\..\路径 有空格\输出 文件.sqlite3" -v -- "..\..\路径 有空格\名字 有空 格.py" 参数1 "参数2 有空格"
```

Sample output:

```
2025-06-21 14:47:28,516 - DEBUG - Preparing to run script with coverage.
2025-06-21 14:47:28,516 - DEBUG - Script path: C:\Users\jifengwu2k\路径 有空格\名字 有空格.py
2025-06-21 14:47:28,516 - DEBUG - Arguments: [u'\u53c2\u65701', u'\u53c2\u65702 \u6709\u7a7a\u683c']
2025-06-21 14:47:28,516 - DEBUG - Coverage output path: C:\Users\jifengwu2k\路径 有空格\输出 文件.sqlite3
2025-06-21 14:47:28,517 - DEBUG - Temporary file for coverage created at: C:\Windows\Temp\tmphulafg
2025-06-21 14:47:28,517 - DEBUG - Launching process:
sys.argv[0]=C:\Users\jifengwu2k\路径 有空格\名字 有空格.py
sys.argv[1]=参数1
sys.argv[2]=参数2 有空格
2025-06-21 14:47:28,678 - INFO - Script exited with code: 0
2025-06-21 14:47:28,680 - DEBUG - Moving temp coverage file to final destination: C:\Users\jifengwu2k\路径 有空格\输出 文件.sqlite3
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
