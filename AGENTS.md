# AGENTS.md

## Contribution workflow

- Follow CONTRIBUTING.md for every change. Open a PR from a separate branch; never push directly to the default branch.
- After opening the PR, wait for feedback from configured automated AI reviewers (currently Codex).
- Critically assess each finding. Fix valid issues, and explain rejected findings explicitly in the PR discussion.
- Check new reviews triggered by updates. Do not merge with unaddressed substantive findings.

## Automatic Code Review Rules

Report only high-confidence P0/P1 issues that:
- Cause significant functional regressions.
- Introduce security vulnerabilities or data loss.
- Can cause serious production failures.

Do not report:
- Style or formatting issues.
- Minor improvements or refactoring suggestions.
- Speculative edge cases.
- Low-impact bugs.
- Missing tests unless they expose a serious risk.

Every finding must describe a concrete failure scenario.
If no qualifying issues exist, report no findings.
