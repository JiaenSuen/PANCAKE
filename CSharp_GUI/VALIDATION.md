# GUI Validation

`VERIFY_GUI.bat` performs a Windows-side build and then launches the application in self-test mode.

The smoke test checks:
- loading a legacy map,
- loading a research map,
- Greedy execution,
- Set Cover execution,
- a short DWOA-AVNS run,
- a short DFOX-APNS run,
- returned route length and finite positive cost.

A successful test writes `SELF-TEST PASSED` to `gui_self_test.log` in the Release output folder. The research comparison itself is reproduced with the Python benchmark because the reported metrics require an exact objective-evaluation budget rather than GUI wall-clock time.
