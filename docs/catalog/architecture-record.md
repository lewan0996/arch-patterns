# Architecture-selection record

[Catalog](README.md) · [Selection route](selection.md) · [Delivery](delivery.md)

The solution-root `architecture.json` records current boundary identities and
explicit selections. Local package `0.3.0` supplies schema version `1`, its pinned
catalog definitions and a read-only validator in `.architecture/`. These files
travel with the solution; resource resolution uses the validator's own directory,
independently of the invoking directory and any catalog checkout.

## Generate and validate

Use the [solution preflight](microservices-solution.md) before `dotnet new`.
A microservices solution starts with its system identity and no hosts. A modular
monolith starts with its separate public host. Generating a service or module
does **not** edit an existing record: after successful manual integration and
applicable build/runtime checks, manually add its identities and selections.
Do not record a partially generated or incompletely integrated addition.

Python 3.10+ and a virtual environment are needed for validation; they are
development tools, not generated application dependencies. From the solution root:

```bash
python3 -m venv /tmp/architecture-validator
/tmp/architecture-validator/bin/python -m pip install -r .architecture/requirements.txt
/tmp/architecture-validator/bin/python .architecture/validate.py architecture.json
```

The command returns `0` on success and `1` for invalid records, with precise
record locations. It performs no writes, repairs, source adoption or network
schema lookup. The schema and catalog release must be supported even when
checking structure alone. A format upgrade and a catalog upgrade each require
explicit review and renewed verification; neither silently changes a record.

## Identity, layout and explicit selections

System, host and module IDs are separate from display names and paths. Initial
IDs may be readable; preserve them across renames and moves. IDs are globally
unique within the record. The solution and all boundary/project paths are
canonical solution-relative paths. No runtime address or secret belongs here.

A flat host has one separately identified module at the same boundary path.
Its API project anchors the shared host/module API; detailed layers are discovered
from source. For example, add this host to `hosts` after creating and verifying
the flat PostgreSQL baseline:

```json
{
  "id": "orders-host",
  "name": "Orders",
  "role": "service",
  "path": "src/Orders",
  "apiProject": "src/Orders/Acme.Orders.API/Acme.Orders.API.csproj",
  "options": { "layout": "single" },
  "modules": [{
    "id": "orders-module",
    "name": "Orders",
    "path": "src/Orders",
    "options": {
      "domainModel": "anemic",
      "applicationFlow": "direct-service",
      "organization": "business-capability"
    },
    "technologies": {
      "database": "postgresql",
      "writePersistence": "ef-core",
      "queryAccess": "ef-core"
    }
  }]
}
```

A monolith host uses `role: monolith`, `layout: modular` and independently located,
named modules. Module identity does not depend on a folder named `Modules`.
Optional module `architectureNotes` links a solution-relative rationale document;
it must not become a competing record. Modular-microservice structure is modeled
but executable support waits for [#60](https://github.com/lewan0996/arch-patterns/issues/60).

BFFs and audience APIs have roles `bff` and `audience-api`, empty `modules`, explicit
`options.clientCredentialSession` (`browser-session` or `bearer-token` respectively),
and a `downstream` array of service/monolith **host IDs**. They have no module
layout or domain/flow selections. Their schema/identity/reference behavior can be
checked with `--structure-only`; the output explicitly says executable support
was not checked. Default validation refuses these still-unverified host roles.
Structure-only success is never permission for a creation action to generate
them. Their runtime/client support belongs to #67 and #68.

## Validation and reconciliation boundary

The JSON Schema checks required properties, readable option values, types and
closed object shapes. Semantic checks enforce unique identities/locations,
composition and layout applicability, sole-module ownership, API anchors,
edge references, and the complete combination against the pinned catalog's
verified selection inventory. Missing choices do not inherit defaults. Known
but unverified domain/flow/database/read combinations are refused by default.

Validation proves record consistency, not agreement with source. Before a future
creation action writes, it must additionally inspect the affected boundary's
projects, dependencies and required host hooks. Report any conflicting recorded
value and source evidence, obtain an explicit reconciliation decision, correct
the intended side within its authorized scope, then recheck. This command never
silently trusts either side or repairs unrelated files. Those action preflights
are delivered by #82–#84.

Actual .NET/package versions, business fields, migration status and implementation
details remain source-owned. Git holds history. Schema validation excludes
timestamps, provenance, duplicated package pins, mutable support flags and
pending-migration fields from the record.

## Evidence and dependencies

`python3 -m unittest discover -s tests -p test_architecture_record.py -v` installs
the package in a disposable CLI home, generates the record and executes the
installed validator from a different directory. It covers stable IDs after
rename/move, flat/modular layouts, edge references, duplicate identities and
locations, invalid paths, missing choices, unsupported versions/combinations,
forbidden source-owned fields and unchanged records after native additions.
These are record/creation checks; they do not certify future edge runtimes or
agent actions. The [validator dependency review](../dependencies/record-increment.md)
records its separate Python graph.

Source: [record resolution](https://github.com/lewan0996/arch-patterns/issues/30#issuecomment-6112277799)
and [implementation #81](https://github.com/lewan0996/arch-patterns/issues/81).
