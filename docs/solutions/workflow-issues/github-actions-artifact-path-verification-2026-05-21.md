---
title: GitHub Actions artifact paths should be visible and verified on the default branch
date: 2026-05-21
category: docs/solutions/workflow-issues
module: Post Merge Lesson Capture
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "Adding or changing a GitHub Actions workflow that publishes artifacts"
  - "Verifying a workflow_dispatch path after a workflow has merged to the default branch"
  - "Keeping read-only workflow outputs metadata-only while still producing downloadable artifacts"
tags: [github-actions, artifacts, workflow-dispatch, post-merge, verification]
---

# GitHub Actions artifact paths should be visible and verified on the default branch

## Context

PR #23 added the Post Merge Lesson Capture workflow. The workflow was intentionally read-only and produced only a job summary plus JSON/Markdown artifacts. The PR branch checks passed, but the first `workflow_dispatch` run on `main` after merge failed during artifact upload.

The report build step succeeded. The upload step failed because the workflow wrote files under `.post-merge-lesson-capture/`, and `actions/upload-artifact@v4` defaults to `include-hidden-files: false`. The action did not upload files from the hidden directory and reported that no files were found.

PR #24 fixed the issue by changing the output directory to `post-merge-lesson-capture/`. A follow-up `workflow_dispatch` run on `main` with `pr_number=23` succeeded, uploaded the JSON/Markdown artifact, kept raw PR title/body/labels/file paths out of the artifact and summary, and retained read-only permissions.

## Guidance

For GitHub Actions workflows that must publish artifacts, prefer an explicit non-hidden output directory:

```yaml
with:
  name: post-merge-lesson-capture
  path: post-merge-lesson-capture/
  if-no-files-found: error
```

Do not use a hidden artifact output directory unless there is a deliberate reason and the workflow explicitly opts into hidden-file upload. In most repository automation, changing the output directory to a visible path is narrower than setting `include-hidden-files: true` because it keeps the artifact target explicit.

Treat artifact generation as two separate checks:

- The workflow produced the report files.
- `actions/upload-artifact` uploaded those files and they can be downloaded.

When a workflow has a `workflow_dispatch` path, verify that path after the workflow is merged to the default branch. A PR branch run proves the branch version can execute, but it does not prove the default-branch operational path works after merge.

## Why This Matters

`Build report success` can hide a broken delivery path. If artifact upload fails, downstream users cannot inspect the durable output even though the report generation step succeeded. This matters most for read-only reporting workflows because their value is the artifact or summary they leave behind.

The safest fix should preserve the existing trust boundary. The artifact path bug did not require new permissions, write tokens, PR comments, issue creation, OpenAI API usage, prompts, or changes to AI Review Gate and auto-merge. The fix only changed where the report files were written.

## When to Apply

- A GitHub Actions workflow writes JSON, Markdown, logs, coverage, screenshots, or other files for artifact upload.
- A workflow uses `workflow_dispatch` and the manual path is part of the supported operating model.
- A report-only or read-only workflow depends on artifacts for human inspection.
- A workflow intentionally avoids raw PR text, secrets, or write side effects and a bugfix must preserve that boundary.

## Examples

Before:

```javascript
const outputDir = ".post-merge-lesson-capture";
```

```yaml
with:
  path: .post-merge-lesson-capture/
```

After:

```javascript
const outputDir = "post-merge-lesson-capture";
```

```yaml
with:
  path: post-merge-lesson-capture/
```

Verification checklist:

- Run the workflow on the default branch with the intended `workflow_dispatch` inputs.
- Confirm the workflow conclusion is `success`.
- Confirm the artifact list contains the expected artifact.
- Download the artifact and check the expected JSON/Markdown files exist.
- Confirm raw PR title/body/labels/file paths are not exported when the workflow promises metadata-only output.
- Confirm token permissions remain read-only and the workflow did not create comments, issues, commits, branches, or pull requests.

## Related

- `docs/POST_MERGE_LESSON_CAPTURE.md`
- PR #23: Infra PR-6 Post Merge Lesson Capture
- PR #24: Post Merge Lesson Capture artifact upload fix
