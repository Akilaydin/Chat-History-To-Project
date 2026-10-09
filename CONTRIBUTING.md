# Contributing

## Pull requests

All contributions, including those from maintainers and coding agents, must go through a pull request. Make changes on a separate branch; do not push directly to the default branch. Keep each PR focused.

Write a clear, self-contained PR title. Keep the description concise (typically 50–100 words) and use the repository's Problem and Solution template. Explain why the change matters and how it addresses the problem, rather than listing modified files. Do not invent claims about impact or metrics.

## Automated AI code review

After opening a PR, wait for feedback from the configured automated AI reviewer(s) (currently Codex). Read the feedback before merging. Treat each finding as a suggestion to assess critically against the code, requirements, and actual failure modes, not as an instruction to follow blindly.

Fix valid, relevant findings and push the changes to the same PR. If a finding is incorrect, irrelevant, or deliberately not adopted, explicitly explain the decision in the PR discussion. Do not silently ignore findings.

If updates trigger a new automated review, evaluate that feedback in the same way. Do not merge while substantive findings remain unaddressed. If the automated review fails or does not arrive, report that limitation instead of treating silence as approval.
