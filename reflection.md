# Reflection — Lab 5: Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues: adding a second blank line between functions, wrapping the 98-character line and removing the unused `logging` import. They are mechanical, local to one line and have no effect on behaviour.

The hardest were the issues no tool reported. Running the program showed that re-registering `FL-01` replaced the Forklift with a Crane, that `change_interval(-30)` made every asset overdue, and that typing a date like `27-10-2026` crashed the program later inside `due_for_inspection`, far from where the bad value entered. Fixing those meant deciding what the correct behaviour should be (reject duplicates? reject future dates?), not just satisfying a rule. The `global` warning was also harder than it looks, because removing it properly meant moving the module-level state into a class and updating every function.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Bandit's B101 (`assert` used) is close to a false positive in context: this is a small demo script that nobody runs with `python -O`, so the assert would never actually be stripped. I still replaced it, because an explicit `if` check states the intent more clearly and costs nothing. Pylint's missing-docstring warnings are similar: for very short, self-explanatory functions they add little, but they are cheap to satisfy and help readers.

The bigger lesson was the opposite problem: false *negatives*. All three tools passed over the duplicate-ID, negative-interval and bad-date bugs, which were the most serious problems in the file.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally, before each commit:** a `pre-commit` hook running Flake8 and Bandit (fast) so style and security issues never reach the repository.
- **In CI:** a GitHub Actions job on every pull request that runs Pylint, Flake8 and Bandit and fails the build if Bandit reports any medium or high issue or the Pylint score drops below a threshold (e.g. 9.5).
- **In the editor:** Pylint/Flake8 integration in VS Code so issues are underlined while typing, which is cheaper than fixing them later.
- **Shared configuration:** a `.pylintrc` / `setup.cfg` in the repo so the whole team uses the same rules, with any deliberate exceptions documented inline.
- **Alongside tests, not instead of them:** unit tests for the behaviour that the tools can't check (duplicate IDs, interval validation, date parsing).

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Robustness:** the program no longer crashes on a badly formatted date; it rejects blank and duplicate IDs, negative intervals and future dates with a clear message instead of corrupting data.
- **Security:** the scratch file is created atomically with `NamedTemporaryFile`, removing the `mktemp` race condition; the empty-registry check no longer depends on `assert`.
- **Correctness:** the registration count is per-registry instead of leaking through a shared default list, and files are always closed and written as UTF-8.
- **Readability and maintainability:** state lives in one `MaintenanceRegistry` class instead of globals, names follow PEP 8, every function has a docstring, and the module can be imported (e.g. by tests) without running `main()`.
- **Measured:** Flake8 went from 12 findings to 0, Bandit from 2 findings to 0, and the Pylint score rose to above the 9.5 target.
