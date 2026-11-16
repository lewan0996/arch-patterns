"""Validate the readable record through its installed, solution-local command."""

import json
import copy
from pathlib import Path
import subprocess
import sys
import tempfile

from test_templates import InstalledPackage


class ArchitectureRecord(InstalledPackage):
    @staticmethod
    def flat_host():
        return {
            "id": "orders-host", "name": "Orders", "path": "src/Orders",
            "apiProject": "src/Orders/Acme.Orders.API/Acme.Orders.API.csproj",
            "role": "service", "options": {"layout": "single"},
            "modules": [{
                "id": "orders-module", "name": "Orders", "path": "src/Orders",
                "options": {"domainModel": "anemic", "applicationFlow": "direct-service",
                            "organization": "business-capability"},
                "technologies": {"database": "postgresql", "writePersistence": "ef-core",
                                 "queryAccess": "ef-core"}
            }]
        }

    def generate(self, root):
        self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                     "--composition", "microservices", "--output", str(root))

    def validate(self, root, *args):
        return subprocess.run([sys.executable, str(root / ".architecture/validate.py"),
                               str(root / "architecture.json"), *args],
                              cwd=root.parent, text=True, capture_output=True, timeout=15)

    def test_fresh_solution_has_pinned_record_and_self_contained_validator(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            record = json.loads((root / "architecture.json").read_text())
            self.assertEqual(1, record["schemaVersion"])
            self.assertEqual({"id": "arch-patterns", "release": "0.3.0"}, record["catalog"])
            self.assertEqual("Commerce.slnx", record["system"]["solutionPath"])
            self.assertEqual({"composition": "microservices"}, record["system"]["options"])
            self.assertEqual([], record["hosts"])
            self.assertNotEqual("Commerce", record["system"]["id"])
            self.assertTrue((root / record["$schema"]).is_file())
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = self.validate(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("valid", result.stdout.lower())
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_flat_host_and_sole_module_have_independent_stable_identities(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            record_path = root / "architecture.json"
            record = json.loads(record_path.read_text())
            record["hosts"] = [self.flat_host()]
            for host_name, boundary in [("Orders", "src/Orders"), ("Purchases", "services/Purchases")]:
                host = record["hosts"][0]
                host.update(name=host_name, path=boundary,
                            apiProject=f"{boundary}/Acme.Purchases.API/Acme.Purchases.API.csproj")
                host["modules"][0].update(name=host_name, path=boundary)
                record_path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("orders-host", host["id"])
                self.assertEqual("orders-module", host["modules"][0]["id"])

    def test_duplicate_boundary_identities_require_explicit_reconciliation(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            original = json.loads(path.read_text())
            original["hosts"] = [self.flat_host()]
            for owner, duplicate_id, pointer in [
                ("host", original["system"]["id"], "/hosts/0/id"),
                ("module", "orders-host", "/hosts/0/modules/0/id")
            ]:
                record = copy.deepcopy(original)
                host = record["hosts"][0]
                (host if owner == "host" else host["modules"][0])["id"] = duplicate_id
                path.write_text(json.dumps(record))
                before = path.read_bytes()
                result = self.validate(root)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(pointer, result.stderr)
                self.assertIn("duplicate identity", result.stderr)
                self.assertEqual(before, path.read_bytes())

    def test_locations_are_relative_unambiguous_and_match_the_selected_layout(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            original = json.loads(path.read_text())
            original["hosts"] = [self.flat_host()]
            for bad_path in ["/tmp/Orders", "../Orders", "src/../Orders", "src//Orders", "C:\\Orders", "src/Orders/"]:
                record = copy.deepcopy(original)
                record["hosts"][0]["path"] = bad_path
                path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertNotEqual(0, result.returncode, bad_path)
                self.assertIn("/hosts/0/path", result.stderr)
            for field, value, diagnostic in [
                ("apiProject", "src/Other/Acme.Orders.API.csproj", "within host"),
                ("modules", [], "exactly one"),
                ("modules", [dict(self.flat_host()["modules"][0], path="src/Other")], "share the host path"),
            ]:
                record = copy.deepcopy(original)
                record["hosts"][0][field] = value
                path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(diagnostic, result.stderr)
            record = copy.deepcopy(original)
            second = self.flat_host()
            second["id"] = "different-host"
            second["modules"][0]["id"] = "different-module"
            record["hosts"].append(second)
            path.write_text(json.dumps(record))
            result = self.validate(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("duplicate location", result.stderr)

    def test_modular_layout_and_edge_references_are_modeled_without_certifying_future_support(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            record = json.loads(path.read_text())
            service = self.flat_host()
            edge = {
                "id": "browser-edge", "name": "Web", "path": "src/Web",
                "apiProject": "src/Web/Acme.Web.API/Acme.Web.API.csproj", "role": "bff",
                "options": {"clientCredentialSession": "browser-session"},
                "modules": [], "downstream": ["orders-host"]
            }
            record["hosts"] = [service, edge]
            path.write_text(json.dumps(record))
            result = self.validate(root, "--structure-only")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("support not checked", result.stdout)
            result = self.validate(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("unverified host role", result.stderr)
            for refs, diagnostic in [(["missing"], "unknown downstream"),
                                     (["orders-host", "orders-host"], "duplicate downstream"),
                                     (["browser-edge"], "downstream service or monolith")]:
                edge["downstream"] = refs
                path.write_text(json.dumps(record))
                result = self.validate(root, "--structure-only")
                self.assertNotEqual(0, result.returncode)
                self.assertIn(diagnostic, result.stderr)
            edge["downstream"] = ["orders-host"]
            edge["modules"] = [dict(service["modules"][0], id="edge-module", path="src/Web")]
            path.write_text(json.dumps(record))
            result = self.validate(root, "--structure-only")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("module-free", result.stderr)

            record["system"]["options"]["composition"] = "modular-monolith"
            service.update(role="monolith", options={"layout": "modular"})
            service["modules"][0]["path"] = "src/Modules/Orders"
            second = copy.deepcopy(service["modules"][0])
            second.update(id="billing-module", name="Billing", path="src/Modules/Billing")
            service["modules"].append(second)
            record["hosts"] = [service]
            path.write_text(json.dumps(record))
            result = self.validate(root)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_unknown_versions_incomplete_choices_and_unverified_combinations_are_refused(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            original = json.loads(path.read_text())
            original["hosts"] = [self.flat_host()]
            changes = [
                (("schemaVersion",), 2, "/schemaVersion"),
                (("catalog", "release"), "future-release", "/catalog/release"),
                (("hosts", 0, "modules", 0, "options", "domainModel"), "unknown", "domainModel"),
                (("hosts", 0, "modules", 0, "technologies", "queryAccess"), "dapper", "unverified selection"),
                (("hosts", 0, "modules", 0, "technologies", "database"), "sql-server", "unverified selection"),
            ]
            for keys, value, diagnostic in changes:
                record = copy.deepcopy(original)
                target = record
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value
                path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertNotEqual(0, result.returncode, keys)
                self.assertIn(diagnostic, result.stderr)
            for model, flow in [("rich", "direct-service")]:
                record = copy.deepcopy(original)
                record["hosts"][0]["modules"][0]["options"].update(domainModel=model, applicationFlow=flow)
                path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertEqual(0, result.returncode, result.stderr)
            record["hosts"][0]["modules"][0]["options"]["applicationFlow"] = "cqrs"
            path.write_text(json.dumps(record))
            result = self.validate(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("unverified selection", result.stderr)

    def test_record_excludes_source_owned_facts_and_requires_explicit_choices(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            original = json.loads(path.read_text())
            original["hosts"] = [self.flat_host()]
            for key in ["supported", "generatedAt", "packageVersion", "migrationGenerationPending", "provenance"]:
                record = copy.deepcopy(original)
                record[key] = "forbidden"
                path.write_text(json.dumps(record))
                result = self.validate(root)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(key, result.stderr)
            record = copy.deepcopy(original)
            del record["hosts"][0]["modules"][0]["technologies"]["queryAccess"]
            path.write_text(json.dumps(record))
            result = self.validate(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("queryAccess", result.stderr)

    def test_native_addition_leaves_the_existing_record_unchanged(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture) / "Commerce"
            self.generate(root)
            path = root / "architecture.json"
            before = path.read_bytes()
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "anemic", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(root / "src/Orders"))
            self.assertEqual(before, path.read_bytes())
