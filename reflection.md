# Reflection — Lab 5: Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 style issues and Pylint's naming and docstring messages. Each message names the exact line and rule (E225, E741, C0103), and the fix is mechanical: add a space, rename `l` to `lowest`, add a docstring. None of them change what the program does.

**Hardest:** the issues that needed a decision rather than an edit.
- **W0621 (redefined-outer-name)** looked like a naming complaint, but the real problem was design: a database connection created at import time as a global. Fixing it properly meant adding `create_connection()`, creating the connection in `main()`, and adding the `if __name__ == "__main__"` guard.
- **B324 (MD5)** needed judgement about *what the hash is for*. Switching to SHA-256 would also have silenced Bandit, but it would change every observer ID. Since the ID is only a short label, `usedforsecurity=False` was the honest fix: it keeps the output the same and documents the intent.
- **Line length** had two different limits (Pylint 100, Flake8 79), so lines that passed Pylint still failed Flake8 and had to be wrapped again.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Partly. **Bandit B324** is the closest to a false positive. MD5 is flagged as "weak hash for security", but here it only turns an observer name into a 6-character display ID. Nothing is protected by it, so there was no real vulnerability. The fix (`usedforsecurity=False`) is a statement of intent rather than a security change.

**Bandit B101 (`assert`)** is similar: in a demo function, an `assert` is harmless. The warning still taught something real, though: asserts vanish under `python -O`, so they shouldn't guard real logic.

Not a false positive: **B608 (SQL injection)**. All the inputs are hard-coded in the demo, so it looked safe, but `log_sighting()` accepts any string, and any caller passing user input would have been injectable.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **In the editor:** run Pylint and Flake8 as linters in VS Code so problems show up while typing, not after.
- **Before each commit:** a `pre-commit` hook that runs Flake8 and Bandit and blocks the commit if they fail, so style and security problems never reach the repository.
- **In CI (e.g. GitHub Actions):** run all three tools on every push and pull request, failing the build if Bandit finds any Medium or High issue or the Pylint score drops below a threshold (for example 9.5).
- **Shared config:** commit a `.pylintrc` and `setup.cfg` (or `pyproject.toml`) so everyone uses the same rules and line length, and suppress justified findings explicitly (`# nosec B324` with a reason) instead of ignoring the tools.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** the SQL injection vulnerability is closed. Values are now passed as parameters, so species or zone names can never be run as SQL.
- **Correctness:** the mutable default argument bug is gone. Each call that doesn't pass `extras` now starts with a fresh dict, so totals can't leak between calls. The sanity check in `main()` now also runs under `python -O`.
- **Structure:** importing the module no longer creates a database or prints output. The connection is created explicitly and passed in, which makes the functions easier to test.
- **Readability:** snake_case names, docstrings on every function, no ambiguous `l`, and lines that fit on screen.
- **Measured:** Pylint went from **3.46/10 to 10.00/10**, Bandit from **3 issues to 0**, and Flake8 from **6 issues to 0**. The program's output is unchanged: `5455c3 25 Leopard`.
