# Creation-only .NET template composition

Research for [Investigate creation-only .NET template composition](https://github.com/lewan0996/arch-patterns/issues/4). Sources checked 2026-09-19. This report establishes capabilities and implementation questions; it does not select the catalog's product design or implement templates.

## Boundary supplied by the user

Generation must create a new solution, microservice, or module in a new folder. Existing solution files, host projects, and configuration remain untouched. Modules own endpoints and are referenced by a shared Web API host. Connecting generated modules to an existing host is therefore a subsequent manual integration step. These are task requirements, not claims about .NET defaults.

## Parameters and conditional output

A custom template consists of source files plus `.template.config/template.json`. The engine supports item, project, and solution templates; a solution template can emit multiple projects. Parameters expose user choices through CLI options, with naming substitutions applying to contents and filenames. Consequently, one invocation can generate a complete service folder containing domain, application, infrastructure, endpoint, and test projects if the catalog eventually selects that structure. This last example is a feasible arrangement, not a prescribed layout. [Microsoft template authoring reference](https://learn.microsoft.com/en-us/dotnet/core/tools/templates).

The configuration supports boolean and choice parameters, computed symbols, file inclusion/exclusion, source modifiers, and renaming. Parameters can be conditionally enabled or required; choice symbols can accept multiple values. These mechanisms can express independently selected ingredients and conditional references within newly generated files. [Template configuration reference](https://github.com/dotnet/templating/wiki/Reference-for-template.json).

Conditional expressions also control content and parameter behavior. Importantly, a disabled parameter is treated as absent, including for required-parameter checks; disabling it should not be treated as guaranteed rejection of an invalid combination. The catalog still needs explicit semantics for incompatible ingredients, rather than merely hiding output branches. [Condition behavior](https://github.com/dotnet/templating/wiki/Conditions).

## Constraints and composition limits

Native template constraints concern execution context: operating system, engine host, installed workloads, SDK version, and project capabilities. They govern whether a template is usable by default; they are not a built-in architecture compatibility matrix. A project-capability constraint can inspect the nearest project, including ancestors, and expects restored SDK-style projects. That behavior is relevant when generation occurs under an existing repository. [Constraint reference](https://github.com/dotnet/templating/wiki/Constraints).

Inference: model ingredient compatibility separately from environmental eligibility. Conditional generation can implement known valid selections, but a clear rejection message before writing may require an orchestration layer or additional validation. Neither the configuration nor constraint references establish an arbitrary dependency solver for architecture ingredients. Whether to introduce a wrapper remains a decision, not a research outcome. [Configuration](https://github.com/dotnet/templating/wiki/Reference-for-template.json), [constraints](https://github.com/dotnet/templating/wiki/Constraints).

A template package is a NuGet package containing one or more templates; installation adds all templates in that package. Local directories, package files, and feeds are supported installation sources. Packaging several entry points together does not itself compose their outputs. The official package tutorial includes authoring MSBuild tasks that validate templates. [Template package tutorial](https://learn.microsoft.com/en-us/dotnet/core/tutorials/cli-templates-create-template-package).

## Preserving existing files

`dotnet new --output` selects the destination. `--dry-run` previews creation effects, while `--force` permits changes that would overwrite existing files. These are useful safeguards, but the documented contract is not “the destination must not already exist.” Thus omitting `--force` alone cannot establish the user's stronger fresh-folder requirement. [CLI reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-new).

Derived implementation requirements, if strict enforcement is desired: reject an existing target even when empty; validate the final resolved destination; reject force mode; check that every planned output stays inside the new folder; and audit every post-action. A wrapper could perform these checks, but a preview is not an atomic guarantee against filesystem changes between inspection and writing. These are proposed safeguards inferred from the boundary, not guarantees supplied by the CLI documentation. The implementation decision must define handling of links, concurrent destination creation, and failure cleanup.

The official post-action registry includes adding project references, adding projects to solutions, editing JSON properties, running scripts, and restoring packages. In particular, the solution-add action can locate a solution in the output directory or its closest parent. Automatically invoking that action while adding a module could modify an existing solution outside the new folder. These capabilities must be considered explicitly when satisfying the creation-only boundary. [Post-action registry](https://github.com/dotnet/templating/wiki/Post-Action-Registry).

The same registry defines a display-manual-instructions action, which can print commands without running them. This supplies a supported way to direct users toward integration after generation. [Manual instructions](https://github.com/dotnet/templating/wiki/Post-Action-Registry#display-manual-instructions).

Proposed integration document contents: projects to add to the existing solution, the host's required project references, service-registration calls, endpoint-mapping calls, configuration keys, and a verification command. Keep that document inside the new module folder. Creating a complete new solution can instead include its own references and host wiring in newly generated files. This distinction follows the user's boundary and does not mandate specific registration method names or APIs.

## Evidence needed before shipping

Microsoft's TemplateVerifier supports snapshotting generated files, checking standard output/error, custom directory verification, and expected command failure. It can run against installed or local templates. Those facilities support output and error-message checks, but a matching snapshot alone does not demonstrate a working architecture. [Template testing tooling](https://github.com/dotnet/templating/wiki/Templates-Testing-Tooling).

Proposed acceptance evidence:

- Install the packaged templates, inspect help, generate every supported combination, and build/test the emitted projects.
- Exercise a running generated API or a temporary host consuming a generated module.
- Generate below an existing solution and compare the pre-existing files before and after, including solution, host, and configuration files.
- Reject an existing empty directory and a populated destination without altering either.
- Verify unsupported ingredient combinations fail before creating files.
- Review generated integration instructions and perform them in a disposable copy, keeping their mutations outside the generation contract.

These checks are proposed future verification criteria. No template or wrapper was executed during this documentation investigation, so SDK-specific behavior, package compatibility, and path-race protection remain unverified experimentally.

## Decisions this research enables

1. Which template entry points share a package, and which ingredient combinations are supported?
2. Is strict creation-only enforcement a wrapper responsibility or a documented caller prerequisite?
3. Which SDKs and hosts must be supported and tested?
4. What module integration contract and manual instructions should generation produce?
5. What evidence is required for each supported combination before publication?
