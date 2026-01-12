Title: ci: add CI workflow + hoisting fixes and tests

Summary
- Add GitHub Actions workflow (.github/workflows/ci.yml) to run unit tests (transpile + C++ syntax-check) on push/PR.
- Strengthen variable hoisting heuristics to avoid hoisting function calls, uppercase constants, and known builtin functions (cos, sin, abs, etc.).
- Add an example transpile test suite (`tests/test_examples_transpile.py`) covering `blink`, `serial_echo`, and `button_led`.
- Add a small smoke test and committed fake Arduino headers for CI (`tests/fake_arduino/*`) to enable syntax-only checks in CI.

Testing
- All tests pass locally: `pytest` -> 2 passed.
- PlatformIO build of generated `boing_ball_amiga` succeeded and firmware uploaded to ESP32 in my run.

Notes
- The branch is pushed: `feature/ci-and-hoist-improvements`.
- To open a PR in the moved repo, visit: https://github.com/xgreenrx-star/Asic-Arduino-Basic-/pull/new/feature/ci-and-hoist-improvements

Please review and tell me if you want me to squash commits before merging or adjust anything else.