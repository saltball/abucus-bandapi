=========
Changelog
=========



Version 0.2.0
=============
Restruction. Now we use state to manage the workflow.

Feature:

- Offer `state` now.
- Offer `task_content` now.

Fix:

- Bugs in kpt.py

Version 0.1.1
=============
Fix abacusworkflow.

Fix:

- kpt generate wrong with numpy.
- CHG file copy logical.
- Unit error in stru.py
- Uncaught situation in generate atomic position lines.
- import error in kpt.py

Feature:

- Add web wait time set for submission. (Override Submission from dpdispatcher)
- Add kpt range and other settings.
- Add flow class, and whole abacusflow.
- New example for abacusflow `flowtest.py`, just need input with machine, resource and matproj id


Version 0.1.0
=============

- Feature: Workflow base class `Workflow`