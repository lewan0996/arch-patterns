"""Read-only validation of the local architecture-selection record, format 1."""

import argparse
import json
from pathlib import Path, PurePosixPath
import sys

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Install validator dependencies from .architecture/requirements.txt in a virtual environment.")


RELEASE = "0.3.0"
RESOURCES = Path(__file__).resolve().parent


def validate(record, *, structure_only=False):
    schema = json.loads((RESOURCES / "architecture.v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    errors = []
    for error in Draft202012Validator(schema).iter_errors(record):
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append(f"{pointer}: {error.message}")
    if errors:
        return sorted(errors)
    catalog = json.loads((RESOURCES / "catalog.json").read_text())
    if catalog["release"] != RELEASE:
        return ["Installed catalog resources disagree with the validator release; reinstall a coherent bundle."]
    if record["catalog"]["release"] != RELEASE:
        errors.append(f"/catalog/release: unsupported release; expected {RELEASE}; explicitly review an upgrade.")
    identities = {record["system"]["id"]: "/system/id"}
    locations = {}

    def relative_path(value, pointer):
        path = PurePosixPath(value)
        if (path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value
                or str(path) != value):
            errors.append(f"{pointer}: use a canonical solution-relative path without traversal.")

    def unique_location(value, pointer):
        if value in locations:
            errors.append(f"{pointer}: duplicate location {value!r}; already at {locations[value]}.")
        else:
            locations[value] = pointer

    relative_path(record["system"]["solutionPath"], "/system/solutionPath")
    hosts_by_id = {host["id"]: host for host in record["hosts"]}
    composition = record["system"]["options"]["composition"]
    monoliths = [host for host in record["hosts"] if host["role"] == "monolith"]
    if composition == "modular-monolith":
        if len(record["hosts"]) != 1 or len(monoliths) != 1:
            errors.append("/hosts: modular-monolith composition requires exactly one monolith host.")
    elif monoliths:
        errors.append("/hosts: a microservices solution cannot contain a monolith host.")
    for host_index, host in enumerate(record["hosts"]):
        pointer = f"/hosts/{host_index}"
        role = host["role"]
        layout = host["options"].get("layout")
        if role in ("bff", "audience-api"):
            if host["modules"]:
                errors.append(f"{pointer}/modules: an edge host must be module-free.")
            credential = "browser-session" if role == "bff" else "bearer-token"
            if host["options"] != {"clientCredentialSession": credential}:
                errors.append(f"{pointer}/options: {role} requires explicit {credential} credentials and no module layout.")
            if "downstream" not in host:
                errors.append(f"{pointer}/downstream: explicit downstream boundary references are required.")
            refs = host.get("downstream", [])
            if len(refs) != len(set(refs)):
                errors.append(f"{pointer}/downstream: duplicate downstream reference.")
            for ref in refs:
                if ref not in hosts_by_id:
                    errors.append(f"{pointer}/downstream: unknown downstream identity {ref!r}.")
                elif hosts_by_id[ref]["role"] not in ("service", "monolith"):
                    errors.append(f"{pointer}/downstream: reference a downstream service or monolith host.")
            if not structure_only:
                errors.append(f"{pointer}/role: unverified host role {role!r} in release {RELEASE}.")
        else:
            if host["options"] != {"layout": layout} or layout is None:
                errors.append(f"{pointer}/options: declare only an explicit service/module layout.")
            if "downstream" in host:
                errors.append(f"{pointer}/downstream: downstream declarations apply only to edge hosts.")
            if role == "monolith" and layout != "modular":
                errors.append(f"{pointer}/options/layout: monolith hosts require modular layout.")
            if role == "service" and layout == "modular" and not host["modules"]:
                errors.append(f"{pointer}/modules: modular service creation requires an initial module.")
            if not structure_only and role == "service" and layout == "modular":
                errors.append(f"{pointer}/options/layout: modular microservice generation is unverified in {RELEASE}.")
        relative_path(host["path"], pointer + "/path")
        relative_path(host["apiProject"], pointer + "/apiProject")
        unique_location(host["path"], pointer + "/path")
        unique_location(host["apiProject"], pointer + "/apiProject")
        if not PurePosixPath(host["apiProject"]).is_relative_to(host["path"]):
            errors.append(f"{pointer}/apiProject: anchor must be within host path.")
        single = host["options"].get("layout") == "single"
        if single and len(host["modules"]) != 1:
            errors.append(f"{pointer}/modules: a flat host requires exactly one sole module.")
        for module_index, module in enumerate(host["modules"]):
            module_pointer = f"{pointer}/modules/{module_index}/path"
            relative_path(module["path"], module_pointer)
            if "architectureNotes" in module:
                relative_path(module["architectureNotes"], f"{pointer}/modules/{module_index}/architectureNotes")
            if not structure_only:
                selections = dict(module["options"], **module["technologies"])
                selected = [selections[key] for key in catalog["moduleSelectionOrder"]]
                supported = catalog["moduleSelections"].get(f"{role}/{layout}", [])
                if selected not in supported:
                    errors.append(f"{pointer}/modules/{module_index}: unverified selection {selections!r} for {role}/{layout} in {RELEASE}.")
            if single:
                if module["path"] != host["path"]:
                    errors.append(f"{module_pointer}: sole module must share the host path.")
            else:
                unique_location(module["path"], module_pointer)
        boundaries = [(pointer, host)] + [
            (f"{pointer}/modules/{index}", module) for index, module in enumerate(host["modules"])]
        for location, boundary in boundaries:
            identity = boundary["id"]
            if identity in identities:
                errors.append(f"{location}/id: duplicate identity {identity!r}; already at {identities[identity]}; reconcile explicitly.")
            else:
                identities[identity] = location + "/id"
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--structure-only", action="store_true",
                        help="Validate identities/applicability/references without claiming executable support.")
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.record.read_text()), structure_only=args.structure_only)
    except (OSError, ValueError) as error:
        print(f"Cannot read record or installed resources: {error}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    scope = "structure valid; executable support not checked" if args.structure_only else "valid"
    print(f"Architecture record {scope} for arch-patterns {RELEASE} (schema 1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
