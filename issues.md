# Issues Found and Fixed — `wildlife_sightings.py`

Reports before and after the fixes are in [`reports/`](reports/).

| Tool | Before | After |
|------|--------|-------|
| Pylint | 3.46/10 (17 messages) | 10.00/10 |
| Bandit | 3 issues (1 High, 1 Medium, 1 Low) | 0 issues |
| Flake8 | 6 issues | 0 issues |

## Issue table

Ordered by severity, high first. Line numbers refer to the original file.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection (Bandit B608, Medium) | Security | 9 | The `INSERT` was built with `str.format`, so a species or zone like `x'); DROP TABLE sightings; --` would be run as SQL. | Use a parameterized query: `VALUES (?, ?, ?)` with the values passed as a tuple. |
| Weak MD5 hash (Bandit B324, High) | Security | 15 | `hashlib.md5` is broken for security use. Here it only builds a short display ID, not a password or signature. | Pass `usedforsecurity=False` to state the intent. The IDs stay the same as before (`Arun` → `5455c3`). |
| Mutable default argument (Pylint W0102) | Bug | 8 | `extras={}` is created once and shared by every call, so totals leak between calls that don't pass their own dict. | Default to `None` and create a new `{}` inside the function. |
| `assert` used for a runtime check (Bandit B101, Low) | Security / Bug | 36 | `assert` is stripped when Python runs with `-O`, so the check silently disappears. | Replace with `if len(totals) != 3: raise RuntimeError(...)`. |
| Global `conn` shadowed by parameters (Pylint W0621) | Design | 4, 8, 18, 26 | A module-level `conn` is created at import time, and every function also takes a parameter named `conn`, hiding the global. | Move setup into `create_connection()`, create the connection in `main()` and pass it in. |
| Demo runs on import | Design | 40 | `main()` was called at module level, so `import wildlife_sightings` ran the demo and created a database. | Guard it with `if __name__ == "__main__":`. |
| Non-snake_case function names (Pylint C0103) | Style | 8, 14, 18 | `logSighting`, `observerId`, `zoneSummary` break PEP 8 naming. | Rename to `log_sighting`, `observer_id`, `zone_summary` and update the callers. |
| Missing docstrings (Pylint C0114/C0116) | Style | 1, 8, 14, 18, 26, 32 | No module docstring and no function docstrings. | Add a one-line docstring to the module and to each function. |
| Unnecessary `else` after `return` (Pylint R1705) | Style | 20–23 | `else:` after a `return` adds nesting for no reason. | Remove the `else` and de-indent `return row[0]`. |
| Ambiguous variable name `l` (Flake8 E741) | Style | 28 | `l` is easy to confuse with `1` and `I`. | Rename to `lowest`. |
| Missing whitespace around operator (Flake8 E225) | Style | 28 | `l=min(...)` | `lowest = min(...)` |
| Lines too long (Flake8 E501, Pylint C0301) | Style | 5, 9, 19, 27 | Lines of 93–117 characters, over Flake8's 79 and Pylint's 100. | Wrap the SQL strings and calls across lines; shorten docstrings. |
| String formatting (Pylint C0209) | Style | 9 | `str.format` where an f-string was suggested. | Removed entirely by the parameterized query (an f-string would still be injectable). |

## Behaviour check

The demo output is unchanged by the fixes. It should print:

```
5455c3 25 Leopard
```

That's the observer ID for `Arun`, the North zone total (1 + 24) and the rarest species.
