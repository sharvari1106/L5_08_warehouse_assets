# Issues Found — `maintenance_system.py`

  **Name:** Sharvari Naik  
  **SRN:** PES1UG24CS431

Line numbers refer to the **original** starter file. Ordered by severity (high and medium first).

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Insecure temp file | Security | Bandit B306 | Medium | 40 | `tempfile.mktemp()` only returns a name; another process can create that file before we open it (race condition / symlink attack). | Use `tempfile.NamedTemporaryFile(..., delete=False)`, which creates the file atomically. |
| 2 | Mutable default argument | Bug | Pylint W0102 | High | 10 | `logs=[]` is created once and shared across every call, so the "registrations this run" count keeps growing as global state. | Removed the default; the log is now `self.registration_log`, created fresh in `__init__`. |
| 3 | Duplicate ID overwrites existing asset | Logic bug | None (found by running) | High | 11, 54 | Registering `FL-01` a second time silently replaced the Forklift with a Crane, losing its data. | `register_asset` rejects IDs that are already registered. |
| 4 | Negative service interval | Logic bug | None (found by running) | High | 29–31, 57 | `change_interval(-30)` makes the overdue threshold negative, so every asset (even ones serviced today) raises an alert. | `change_interval` rejects non-positive values and keeps the current interval. |
| 5 | Unvalidated date crashes program | Logic bug | None (found by running) | High | 17, 24, 58–60 | Entering `27-10-2026` is stored as-is, then `strptime` in `due_for_inspection` raises `ValueError` and the program crashes. | Validate with `strptime` before storing; reject bad formats and future dates with a message. |
| 6 | Bare `except` | Bug | Pylint W0702, Flake8 E722 | Medium | 18 | Catches everything, including `KeyboardInterrupt` and typos in the code, hiding real errors. | Check `asset_id in self.assets` explicitly; catch only `ValueError` for date parsing. |
| 7 | Empty asset ID accepted | Logic bug | None (found by running) | Medium | 53 | `register_asset("", ...)` creates an asset with a blank ID. | Strip the ID and reject it if empty. |
| 8 | `global` statement / module state | Design | Pylint W0603 | Medium | 7, 29–31 | Mutable globals make the code hard to test and reason about. | Moved state into a `MaintenanceRegistry` class. |
| 9 | Files opened without `with` / encoding | Bug | Pylint R1732, W1514 | Medium | 34–36, 41–43 | File isn't closed if `write` raises; encoding depends on the OS. | `with open(file, "w", encoding="utf-8")` and `json.dump`. |
| 10 | `assert` for runtime check | Security | Bandit B101 | Low | 61 | Asserts are removed under `python -O`, so the check disappears. | Replaced with an explicit `if not assets:` check. |
| 11 | Unused import | Style | Pylint W0611, Flake8 F401 | Low | 2 | `logging` is imported but never used. | Removed. |
| 12 | Non-snake_case name | Style | Pylint C0103 | Low | 46 | `printAlerts` breaks PEP 8 naming. | Renamed to `print_alerts`. |
| 13 | Missing docstrings | Style | Pylint C0114/C0116 | Low | 1, all functions | No module or function docstrings. | Added docstrings. |
| 14 | Blank lines / line length | Style | Flake8 E302, E305, E501 | Low | 10–50, 66, 11 | One blank line between top-level functions; line 11 is 98 characters. | Two blank lines between definitions; wrapped long lines. |
| 15 | Code runs on import | Design | — | Low | 66 | `main()` runs whenever the module is imported. | Wrapped in `if __name__ == "__main__":`. |

## Commits

1. **Bandit** — fixes #1 and #10.
2. **Flake8** — fixes #6 (narrowed except), #11, #14.
3. **Pylint + logic** — fixes #2, #3, #4, #5, #7, #8, #9, #12, #13, #15.
