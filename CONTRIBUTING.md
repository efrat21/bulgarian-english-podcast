Branch naming

- Use branch names: `squad/{issue-number}-{kebab-case-slug}` (e.g., `squad/1-setup-build`).

Pull requests

- Open PRs against `main`.
- Include `Closes #<issue-number>` in the PR body when relevant.
- Include the Co-authored-by trailer in commits:

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

- Use draft PRs while work is in progress.

Testing and formatting

- Run tests: `python -m unittest discover -s tests -v`
- Follow `.editorconfig` for formatting.
