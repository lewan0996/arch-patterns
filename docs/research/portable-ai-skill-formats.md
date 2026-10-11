# Portable AI skill formats

Research date: **2026-10-11**. Scope: [Investigate portable AI skill formats across agent platforms (#26)](https://github.com/lewan0996/arch-patterns/issues/26). This is documentation research, not an installation or execution compatibility test. Packaging policy belongs to [Specify portable action-skill packaging and compatibility (#27)](https://github.com/lewan0996/arch-patterns/issues/27).

The reusable part is an action's Markdown instructions and supporting content. A shared file format does not establish identical discovery, invocation, metadata interpretation, tool access, or behavior. The catalog and `architecture.json` architecture-selection record can remain agent-neutral; platform integration can supply the environment around the action. This is a portability assessment, not a decision about copies, symlinks, generated adapters, plugins, installers, or supported versions.

## Common format and its limits

The [Agent Skills specification](https://agentskills.io/specification) defines a directory containing `SKILL.md`: YAML frontmatter followed by Markdown. `name` and `description` are required. Names match their directory, use lowercase alphanumerics and single hyphens, and are 1–64 characters; descriptions are 1–1024 characters. Optional standard fields are `license`, `compatibility` (environment requirements, at most 500 characters), `metadata` (string-to-string map), and experimental `allowed-tools`. The latter explicitly has implementation-dependent support.

The same specification permits supplementary files, conventionally `scripts/`, `references/`, and `assets/`, and defines relative references from the skill root. Instructions and resources load progressively; its 500-line/5,000-token guidance is authoring guidance, not a universal enforced runtime limit. Script language support depends on the host. Neither `compatibility` text nor a file in `scripts/` installs a dependency. [Format and resource specification](https://agentskills.io/specification).

## Discovery, invocation, and installation

Each path below contains `<name>/SKILL.md`; repository locations are relative to the repository or applicable working directory. These are documented discovery locations, not this project's chosen layout.

| Platform | Discovery and invocation | Local installation paths and scopes |
| --- | --- | --- |
| Codex CLI / IDE | Description matching; explicit `$name` or `/skills`. Metadata loads before the body. | Repository `.agents/skills`; personal `~/.agents/skills`; administrator `/etc/codex/skills`; bundled system skills. Symlinked skill folders are supported. [Codex skills](https://learn.chatgpt.com/docs/build-skills). |
| Claude Code | Description matching or `/name`; plugin invocation is namespaced. | Project `.claude/skills`; personal `~/.claude/skills`; enterprise `.claude/skills` under the managed settings directory; `.claude/skills` in `--add-dir` directories; plugin `skills/`. [Claude Code skills](https://code.claude.com/docs/en/skills). |
| OpenCode | Native `skill` tool loads the selected skill. Optional metadata exposes `/name` in the TUI. | Project `.opencode/skills`, `.claude/skills`, `.agents/skills`; personal `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills`. [OpenCode skills](https://opencode.ai/docs/skills/). |
| GitHub Copilot | Description matching; CLI and VS Code also support `/name`. | GitHub's common/CLI docs list project `.github/skills`, `.claude/skills`, `.agents/skills`; personal `~/.copilot/skills`, `~/.agents/skills`. VS Code additionally lists personal `~/.claude/skills`. [CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills), [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills). |

Monorepo behavior is material:

- **Codex** scans from the launch directory upward to the repository root. Root skills reach subdirectory sessions; this is not a documented recursive scan of all child packages. Duplicate names are not merged and can both appear in selectors. [Codex discovery](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills).
- **Claude Code** scans ancestors to the repository root and loads descendant skills when it first reads or edits files there. Nested collisions can remain available under directory-qualified commands. Linked worktrees have a root boundary; the documented main-checkout fallback requires v2.1.277+. Enterprise/personal/project skill folders can be symlinks; identical targets are loaded once. Plugin symlink handling differs. [Claude discovery](https://code.claude.com/docs/en/skills#discovery-from-parent-and-nested-directories).
- **OpenCode** scans ancestors from CWD to the Git worktree boundary. Its troubleshooting guidance asks for unique names across locations; the skills page does not establish a collision-precedence contract. [OpenCode discovery](https://opencode.ai/docs/skills/#understand-discovery).
- **VS Code** documents `chat.useCustomizationsInParentRepositories` for parent-repository skills when opening a monorepo subfolder. Do not project that setting onto Copilot CLI or cloud discovery. [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills).

The overlap in `.agents/skills` recognition does not establish four-platform discovery: Claude Code's listed local locations use `.claude/skills`. Likewise, legacy Codex `.codex/skills` examples or the installed system-skill location are not substitutes for the current documented repository paths. [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills).

## Metadata and nonportable behavior

| Platform | Documented recognition beyond the common body |
| --- | --- |
| Codex | Requires `name` and `description`; optional **separate** `agents/openai.yaml` defines `interface`, invocation `policy.allow_implicit_invocation`, and `dependencies.tools`. These are not shared `SKILL.md` frontmatter fields. Setting implicit invocation false preserves explicit invocation. [Codex metadata](https://learn.chatgpt.com/docs/build-skills#optional-metadata). |
| Claude Code | Accepts omitted name/description with fallbacks, unlike the standard's required fields. Extensions include `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`. `metadata`, `license`, and `compatibility` do not drive Claude behavior. [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference). |
| OpenCode | Lists `name`, `description`, `license`, `compatibility`, `metadata`. Its behavioral keys are `metadata["opencode/slash"]: "true"` and `metadata["opencode/autoinvoke"]: "false"`. The latter hides auto-selection guidance but permits manual/exact-name loading. Use string values to match the standard. [OpenCode frontmatter](https://opencode.ai/docs/skills/#write-frontmatter). |
| Copilot | GitHub's common guide documents required `name`/`description`, optional `license`, and `allowed-tools`. VS Code additionally documents `argument-hint`, `user-invocable`, `disable-model-invocation`, and `context: fork`; forked execution requires `github.copilot.chat.skillTool.enabled`. That does not establish CLI/cloud parity for those fields. [GitHub guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills), [VS Code format](https://code.visualstudio.com/docs/agent-customization/agent-skills#_skillmd-file-format). |

Recognizing a standard field is different from enforcing it. Absence from a platform's field table is recorded here as **not established**, rather than proof of rejection or support. A shared `metadata` map can carry vendor keys without making their semantics portable. No cross-platform meaning is established for a model name, hook, subagent type, argument substitution, or tool identifier.

## Referenced files, scripts, and permissions

| Platform | Supporting content and execution boundary |
| --- | --- |
| Codex | Supports optional scripts/references/assets. Its sandbox constrains spawned commands, filesystem access, and networking; approval policy is a separate control. Tool-dependency metadata does not itself prove a working connection or permission. [Skills](https://learn.chatgpt.com/docs/build-skills), [sandbox](https://learn.chatgpt.com/docs/sandboxing). |
| Claude Code | Supports referenced files, `$ARGUMENTS`/positional substitutions, `${CLAUDE_SKILL_DIR}`, and shell-output injection. These body features need adaptation elsewhere. `allowed-tools` pre-approves tools for the invoking turn; it is not an exclusive tool allowlist. Managed policy can suppress these grants. [Claude Code execution controls](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill). |
| OpenCode | The `skill` tool returns instructions; normal read/shell/edit tools do work. `permission.skill` controls loading, separately from `bash`, `edit`, and `external_directory` permissions. A load grant is not a script-execution grant. The inspected skills guide does not establish Claude-style substitution or `allowed-tools` semantics. [Tools](https://opencode.ai/docs/tools/#skill), [permissions](https://opencode.ai/docs/permissions/). |
| Copilot | GitHub's CLI guide describes bundled scripts, an explicit skill-base-directory invocation, and optional `allowed-tools` pre-approval (example tool `shell`). VS Code supports relative Markdown links and `#file:` references; its terminal/tool approvals and sandbox remain surface-specific controls. Do not assume identical `allowed-tools` enforcement across all Copilot surfaces. [CLI scripts](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills#enabling-a-skill-to-run-a-script), [VS Code resources](https://code.visualstudio.com/docs/agent-customization/agent-skills), [VS Code permissions](https://code.visualstudio.com/docs/agents/run/approvals). |

For this catalog, a portable instruction can say “resolve `references/…` relative to this skill's directory” and separately identify the target solution/module directory. A shell working directory is not automatically the skill directory. An adapter must preserve or resolve these two roots, provide the required tools and .NET SDK/templates, and respect host permissions. This is an inference from the resource and execution models above; no installed layout or script has been tested.

The existence of a script means the agent can be instructed to use it. Successful execution additionally requires a runtime, dependencies, permitted paths, and any required network access. A skill does not itself provide any of these. Similarly, `allowed-tools` contains product-specific tool names: a Claude `Bash(...)` rule cannot be treated as a Copilot `shell` grant or an OpenCode `permission.bash` rule. [Standard's experimental field](https://agentskills.io/specification#allowed-tools-field), [OpenCode permissions](https://opencode.ai/docs/permissions/), [Copilot script guidance](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills#enabling-a-skill-to-run-a-script).

## Copilot surfaces and version boundaries

“Copilot supports skills” is too broad to describe an execution target. The current [support overview](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) names cloud agent, code review, CLI, the Copilot app, VS Code agent mode, and JetBrains agent mode. It does not imply that every Copilot Chat integration supports skills, or that a review surface can execute this catalog's creation actions.

| Surface/tool | Established by the inspected sources | Limit of this research |
| --- | --- | --- |
| VS Code agent mode | Skills became generally available in **1.109**. Current docs describe slash invocation, parent-repository discovery and fork controls. [1.109 release](https://code.visualstudio.com/updates/v1_109#_agent-skills-are-generally-available). | GA in 1.109 does not date every later field or setting to that version. |
| JetBrains agent mode | GitHub announced skills GA on **2026-06-02**. [Release announcement](https://github.blog/changelog/2026-06-02-introducing-copilot-cli-and-agentic-capabilities-enhancements-in-jetbrains-ides/). | No minimum plugin build or full metadata/path parity was established. |
| Copilot CLI | Current guide documents `/skills list`, `/skills info`, `/skills add`, `/skills reload`, and explicit `/name` use. [CLI guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills). | No minimum CLI build or ancestor-scan algorithm was established. |
| Cloud agent, code review, Copilot app | Named in the current support overview. [Supported surfaces](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills). | A local personal directory is not evidence of availability in a remote session; per-surface execution and provisioning need verification. |
| GitHub CLI skill installer | `gh skill` is public preview, requires **gh 2.90.0+**, supports agent/scope selection and pinned installs. [Installation guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#managing-skills-with-github-cli). | This is an installer version, not the minimum version for skill consumption. No installer was run. |

The VS Code docs also describe experimental Codex-on-Agent-Host discovery of `.github/skills`. That integration-specific behavior must not be reported as native Codex CLI discovery. [VS Code integration note](https://code.visualstudio.com/docs/agent-customization/agent-skills#_create-a-skill).

## Reuse boundary for architecture actions

The following is a mapping of the agreed catalog scope, not new packaging policy. Action names are `start-project`, `add-microservice`, `add-module`, `add-aggregate`, and `add-entity`; a module remains an internal boundary within a deployable host as defined in [CONTEXT.md](../../CONTEXT.md).

| Content | Reuse assessment |
| --- | --- |
| Action purpose, required inputs, applicability, boundary identity, selected options and validation outcomes | Agent-neutral prose can be reused verbatim. It describes the catalog's domain rather than an agent API. |
| Read `architecture.json`, select the intended system/host/module, detect selection drift, and preserve unrelated work | Can be identical instructions. Access to the target repository and resolution of its root remain runtime prerequisites. |
| Use `dotnet new` for creation in a new folder; make bounded changes in an existing module | Can be identical action semantics and CLI argument guidance once template names/options are specified. This does not guarantee installed templates, shell quoting portability, or permission to run the command. |
| Add-aggregate requires a rich domain model; add-entity targets an existing aggregate or an anemic data entity as applicable | The domain distinction can remain verbatim across agents; discovery metadata must accurately describe those boundaries. |
| Relative reference Markdown and deterministic helper logic | Reusable if the packaged resources and declared runtimes are preserved. A reference to an absent catalog checkout will not become available merely because a skill was discovered. |
| Install location, explicit invocation syntax, trigger controls, permission/tool names, model/subagent settings, host variables and dynamic substitutions | Need platform-specific instructions or an adapter if the action uses them. A common body can avoid depending on them, but this report does not choose how. |

For example, the following original action text has no platform binding:

> Locate the solution's architecture-selection record. Resolve the selected module by its boundary identity and confirm its recorded location and domain-model option. For add-aggregate, require a rich domain model and add only the explicitly requested behavior. Preserve unrelated changes and report the verification result.

Its portability is a content-level assessment. Proving that each agent follows it requires runtime evaluation; it is not demonstrated by this research.

## Remaining verification and documentation gaps

- No skill was installed or invoked on any of the four platforms, and no script, template, or generated .NET application was executed. No runtime compatibility verdict is claimed.
- Current live documentation is a dated observation, not a pinned release contract. Minimum supported versions, desired Copilot surfaces, and release verification remain downstream decisions.
- Codex's skill-list budget can shorten descriptions or omit entries in large installations. Discovery does not ensure invocation. [Codex disclosure limits](https://learn.chatgpt.com/docs/build-skills).
- The inspected pages do not establish every host's handling of unknown metadata, duplicate names, symlinks, hot reload, or externally shared references. Where documented above, behavior applies only to that platform/surface.
- A future compatibility check needs real root/subfolder discovery, explicit and implicit invocation, relative-resource resolution from a different CWD, permitted/denied script execution, and architecture-action output verification. This identifies evidence gaps rather than specifying packaging or an implementation plan.

## Research validation record

The local capability check used `command -v codex`, `codex --version`, and `codex --help`: the executable was `/home/linuxbrew/.linuxbrew/bin/codex`, reporting **codex-cli 0.162.1**. Help confirmed CLI plugin/MCP management and sandbox/approval options. No configuration or credentials were printed. This establishes the inspected local executable only, not its skill compatibility. The available tool surface contained general web retrieval but no dedicated OpenAI documentation tool; official OpenAI pages supplied the feature contract.

Primary pages were opened with web retrieval and, where useful, their official Markdown representations were fetched with `curl -fsSL`. The old OpenAI `/codex/skills/` URL redirected to the cited ChatGPT Learn page. Failed speculative Markdown/URL fetches were replaced by successful canonical HTML/Markdown retrievals; they are not evidence of missing product support.

Manual citation review checked each platform's paths, invocation and fields against its own fetched documentation. It specifically separated standard fields from platform recognition, skills from tool permission, VS Code settings from CLI/cloud behavior, and content reuse from runtime proof. Repository scope review found no ADR directory and used the existing single-context vocabulary. Only this report was edited by the research worker.

The machine-checked source retrieval and artifact checks below are recorded after the final content pass.


Validation run: **2026-10-11**. For each unique primary-source URL below, the invocation was `curl -sS -L --fail --max-time 30 -w "\n%{http_code}\n%{url_effective}" URL`. Success required exit 0, final HTTP 200, and a nonempty response body. All 14 passed. The byte counts record the fetched HTML, not an execution trace.

| Primary source | HTTP | Captured response bytes |
| --- | --- | ---: |
| https://agentskills.io/specification | 200 | 446855 |
| https://code.claude.com/docs/en/skills | 200 | 1204918 |
| https://code.visualstudio.com/docs/agent-customization/agent-skills | 200 | 152669 |
| https://code.visualstudio.com/docs/agents/run/approvals | 200 | 143897 |
| https://code.visualstudio.com/updates/v1_109 | 200 | 265627 |
| https://docs.github.com/en/copilot/concepts/agents/about-agent-skills | 200 | 557888 |
| https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills | 200 | 622676 |
| https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills | 200 | 660722 |
| https://github.blog/changelog/2026-06-02-introducing-copilot-cli-and-agentic-capabilities-enhancements-in-jetbrains-ides/ | 200 | 119193 |
| https://learn.chatgpt.com/docs/build-skills | 200 | 407803 |
| https://learn.chatgpt.com/docs/sandboxing | 200 | 480793 |
| https://opencode.ai/docs/permissions/ | 200 | 89936 |
| https://opencode.ai/docs/skills/ | 200 | 73290 |
| https://opencode.ai/docs/tools/ | 200 | 97451 |

Artifact checks: a Python `pathlib`/`re` check confirmed all eight comparison/validation sections and the local `CONTEXT.md` reference; `git diff --check -- docs/research/portable-ai-skill-formats.md` exited 0. The report is new/untracked, so the diff check alone does not validate its contents. Citation support and scope were reviewed manually as described above. Captured artifact: `docs/research/portable-ai-skill-formats.md` (this document). Tracker URLs identify scope; they were not used as external evidence for platform behavior.

Fragment validation: fetched each cited page with `curl -fsSL --max-time 30 URL` and compared all 14 cited fragments against HTML `id`/`name` attributes using Python regular expressions. **14/14 passed** after correcting two VS Code anchors to include their leading underscore. Codex `where-to-save-skills` and Claude `discovery-from-parent-and-nested-directories` remain explicit IDs despite renamed visible headings. Final text check: nonempty report, 14 HTTP-result rows, local context link exists, no trailing whitespace, and balanced code fences.
