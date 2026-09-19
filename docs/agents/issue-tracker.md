# Issue tracker: GitHub

Issues and specs for this repo live in GitHub Issues. Use `gh` from this clone; it infers `lewan0996/arch-patterns` from the remote.

## Conventions

- Create issues with `gh issue create`.
- Read issues and comments with `gh issue view <number> --comments`.
- List issues with `gh issue list`, filtering by state and labels as needed.
- Comment with `gh issue comment <number>`.
- Add or remove labels with `gh issue edit <number>`.
- Close issues with `gh issue close <number>`.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Skill instructions

- “Publish to the issue tracker” means create a GitHub issue.
- “Fetch the relevant ticket” means read the GitHub issue and comments.

## Wayfinding

Use one issue labelled `wayfinder:map` as the map and GitHub sub-issues as child tickets. If sub-issues are unavailable, link children from a task list in the map. Record blockers with native issue dependencies when available, otherwise with a `Blocked by: #<number>` line. An unassigned child with no open blockers is ready to claim.
