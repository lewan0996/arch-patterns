# Contract baselines and justified breaking changes

Status: deferred by the owner on 2026-10-17. Contract testing is excluded from the current pattern library. [Consider optional contract testing and compatibility tooling](https://github.com/lewan0996/arch-patterns/issues/34) preserves the future question; [the scope decision](https://github.com/lewan0996/arch-patterns/issues/33#issuecomment-6241288687) supersedes the earlier testing requirement. The workflow below remains a research proposal, not an accepted implementation requirement.

Research date: 2026-10-17. Scope: structural public HTTP API and event contracts. Directly referenced module commands/queries and behavioral-change detection are excluded by the current discussion. These findings support a decision; no tools were installed or exercised against a generated application.

## Established patterns

### Semantic comparison with documented exceptions: oasdiff

`oasdiff breaking` compares two OpenAPI documents, reports incompatible changes, and can fail according to severity. It distinguishes request and response compatibility; for example, making an input property required can invalidate previously valid requests. Its JSON output supports a test wrapper. [Breaking-change documentation](https://github.com/oasdiff/oasdiff/blob/f0a200d76c304db65b592ae4a4f920fd0478455c/docs/BREAKING-CHANGES.md).

Individual findings can be accepted using `--err-ignore` / `--warn-ignore`. Each matching line contains an HTTP method/path and the change description; extra prose is allowed. The file can be Markdown and document other changes, so a version log can serve directly as an exception file. This is more precise than disabling a rule globally. These matching rules do not themselves enforce the proposed log's old/new versions, reason, migration instructions, or parallel-version requirement. [Ignoring specific changes](https://github.com/oasdiff/oasdiff/blob/f0a200d76c304db65b592ae4a4f920fd0478455c/docs/BREAKING-CHANGES.md#ignoring-specific-breaking-changes).

Git operands such as `main:openapi.yml` support comparing against another branch instead of a baseline editable in the current checkout. [Official migration guide](https://www.oasdiff.com/docs/migrate-from-optic).

### Explicit snapshot acceptance: Verify

Verify compares test output with a `.verified.` file. A mismatch fails and produces a `.received.` file. A developer accepts the output by replacing the verified file; the next run uses that updated reference. Verified files belong in source control; received files do not. This directly answers how an accepted baseline becomes the next baseline. [Verify workflow and conventions](https://github.com/VerifyTests/Verify/blob/db6185ac25223febaf1be559f2221df84278248b/readme.md#initial-verification).

Limitation: plain snapshot equality rejects compatible additions too, and accepting the snapshot does not require a justification. Verify can help review deterministic contract output, but a semantic comparator plus project-specific log checks is needed for the requested compatibility policy. This limitation is an inference from its documented equality workflow.

### Suppress now, advance baseline later: ApiCompat precedent

Microsoft's .NET compatibility tooling supports intentional-change suppression files. The documented XML identifies diagnostics, targets, and comparison operands. It does not document a built-in justification field. This checks .NET assemblies/packages rather than HTTP or event schemas; it is a workflow analogy, not a recommended wire-contract checker. [Microsoft suppression format](https://learn.microsoft.com/en-us/dotnet/fundamentals/apicompat/diagnostic-ids#suppression-file).

A concrete first-party application is Microsoft Agent Framework: an approved intentional break gets a generated suppression file included in its PR with justification. After release, maintainers delete suppressions and update the baseline version to the newly published package. Thus exceptions bridge a specific comparison, while advancing the baseline prevents the same accepted difference recurring indefinitely. [Agent Framework contribution workflow](https://github.com/microsoft/agent-framework/blob/44fe223da7ea6853eefb7053e25c2c213a2e5c15/CONTRIBUTING.md#automated-api-compatibility-validation).

### Event schemas: latest versus retained history

Confluent's compatibility modes distinguish new consumers reading old messages (`BACKWARD`) from old consumers reading new messages (`FORWARD`); `FULL` checks both. Non-transitive modes compare with the latest registered schema; transitive modes compare against all previous schemas. Checking compatibility and registering a schema are separate API operations. [Compatibility concepts and test endpoints](https://docs.confluent.io/platform/current/schema-registry/develop/api.html#compatibility).

This exposes an additional event concern: advancing the latest baseline does not necessarily prove compatibility with every retained historical message. Select the history window and direction explicitly; do not assume adjacent compatible updates imply compatibility with all older data. Registry schema revision numbers also should not be confused with the public event's major version. The latter distinction is a proposed project convention, not a claim that the registry enforces it.

## Proposed workflow for this repository

The following is a synthesis, not an off-the-shelf feature promised by the sources.

1. Commit deterministic contract documents by public contract identity and major version, plus a version log. Treat the target branch's committed documents at a known revision as the previously accepted baseline. A local run can read the same baseline from Git; CI only runs the tests with that revision available.
2. Tests generate current contracts and compare them semantically with the trusted previous baseline. Compatible structural changes pass. Do not use raw snapshot equality as the compatibility decision. Validate candidate committed documents against generated output separately so an outdated document cannot masquerade as the implementation.
3. For a breaking successor, add a parallel major version and its document, retaining the old public version and its compatibility checks. Compare the predecessor to the new version to identify the deliberate differences for the version log. The predecessor's own implementation must remain compatible; a justification cannot waive that requirement.
4. Require each detected cross-version break to match a log entry containing contract identity, old/new versions, affected operation/field, reason, and migration instructions. Bind acceptance to the specific transition, ideally with before/after document hashes and stable finding identities. Reject unrelated or stale entries. Tools can check presence and matching; a meaningful reason remains a review judgment.
5. Commit the generated documents and justification together. Until merge, compare against the previous target-branch documents, even if the PR updates its own snapshots. This prevents regeneration from erasing the evidence that approval was needed. CI never accepts or commits a baseline itself.
6. Merge advances the accepted baseline naturally: subsequent comparisons read the merged documents, so the previously accepted introduction stops recurring. Keep the log as history and continue checking every supported old version. Event histories may require additional retained schemas for transitive checks.

The remaining design choice is the event schema format and comparator. The sources establish the workflow, but do not select a universal event compatibility algorithm. A schema registry is an optional implementation choice, not a prerequisite for repository-based tests.

## Integrated-tool fit

Follow-up research: an established implementation exists for each major mechanism, but no exact integrated match was verified among the candidates below. This is a bounded finding about reviewed documentation, not proof that no such product exists.

| Candidate | Established capability | Gap against this discussion |
| --- | --- | --- |
| oasdiff | Structural OpenAPI comparison; Git revision operands; individual findings accepted through a prose Markdown file. | OpenAPI-specific. Its native exception matching requires method/path and change description, not the proposed reason/migration/version fields or an exact before/after baseline pair. Baseline advancement comes from selecting the updated Git baseline after merge. |
| Specmatic | One backward-compatibility command for OpenAPI and AsyncAPI, including branch comparison. | AsyncAPI compatibility is commercial. The documented WIP operation tag bypasses build failure while retaining feedback; this is broader than accepting one justified difference. No matching-justification-log acceptance mechanism was found in the reviewed documentation. |
| Pact / PactNet | Contract testing for HTTP and asynchronous messages; Broker tracks versioned contracts and verification results. | Consumer-driven examples rather than complete structural schema comparison. Pending pacts transition through successful verification, not an approved justification log; `can-i-deploy` evaluates the consumer/provider verification matrix. |

For oasdiff's actual exception syntax, see [native Markdown ignores](https://github.com/oasdiff/oasdiff/blob/f0a200d76c304db65b592ae4a4f920fd0478455c/docs/BREAKING-CHANGES.md#ignoring-specific-breaking-changes) and [Git comparison](https://www.oasdiff.com/docs/migrate-from-optic). Specmatic documents [branch baselines and WIP handling](https://docs.specmatic.io/contract_driven_development/backward_compatibility.html), [AsyncAPI rules](https://docs.specmatic.io/contract_driven_development/backward_compatibility_rules.html), and [commercial boundaries](https://docs.specmatic.io/references/open-source-vs-enterprise). Pact documents its [example-based approach](https://docs.pact.io/), [PactNet messages](https://docs.pact.io/implementation_guides/net/docs/messaging-pacts), [pending-contract acceptance](https://docs.pact.io/pact_broker/advanced_topics/pending_pacts), and [deployment matrix](https://docs.pact.io/pact_broker/can_i_deploy).

Optic was also checked: its repository is archived, read-only since 2026-01-12, so it is not a good new dependency recommendation. [Optic repository](https://github.com/opticdev/optic). There is direct adoption evidence for oasdiff: Backstage's own release notes describe replacing Optic with oasdiff for OpenAPI breaking-change detection. [Backstage release notes](https://github.com/backstage/backstage/blob/master/docs/releases/v1.53.0-next.2-changelog.md). This supports calling oasdiff established; it does not establish a popularity ranking.

Practical fit: reuse oasdiff for HTTP comparison and its Markdown exceptions, adding a small test wrapper for this project's required log fields and transition binding. For a single product covering HTTP and event schema checks, Specmatic Enterprise deserves consideration, but the justification-log rule still requires project integration based on the documentation reviewed. A registry's compatibility override similarly is not evidence of an exact logged-justification workflow; changing a compatibility mode must not silently waive the old public version's guarantees.
