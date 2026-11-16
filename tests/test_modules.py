"""Installed native modular-monolith and named-module creation chains."""

from pathlib import Path
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import unittest

from test_templates import InstalledPackage, REPO


class ModuleTemplates(InstalledPackage):
    def test_modular_monolith_creates_one_operational_public_host(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                         "--composition", "modular-monolith", "--output", str(system))
            host = system / "src/Commerce/Acme.Commerce.API"
            self.assertTrue((host / "Program.cs").is_file())
            self.assertEqual([host / "Acme.Commerce.API.csproj"], list(system.glob("src/*/*/*.csproj")))
            self.assertFalse((host.parent / "Modules").exists())
            listing = self.run_cli("sln", "Commerce.slnx", "list", cwd=system)
            self.assertIn("Acme.Commerce.API.csproj", listing)
            self.run_cli("restore", "Commerce.slnx", cwd=system)
            self.run_cli("build", "Commerce.slnx", "--no-restore", "--warnaserror", cwd=system)
            self.run_cli("test", "Commerce.slnx", "--no-build", cwd=system)

    def test_initial_and_later_modules_integrate_only_by_explicit_host_edits(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                         "--composition", "modular-monolith", "--output", str(system))
            boundary = system / "src/Commerce"
            host = boundary / "Acme.Commerce.API"
            record = system / "architecture.json"
            if not record.exists():
                record.write_text('{"fixture":"preserve"}\n')
            for name in ("Orders", "Billing"):
                before = {p: p.read_bytes() for p in system.rglob("*") if p.is_file()}
                module = boundary / "Modules" / name
                self.run_cli("new", "arch-module", "--name", name, "--rootNamespace", "Acme.Commerce",
                             "--domainModel", "anemic", "--applicationFlow", "direct-service",
                             "--database", "postgresql", "--output", str(module))
                self.assertEqual(before, {p: p.read_bytes() for p in before})
                self.assertEqual(5, len(list(module.glob("*/*.csproj"))))
                self.assertFalse((module / f"Acme.Commerce.{name}.API/Program.cs").exists())
                self.assertFalse((module / "Dockerfile").exists())
                self.assertIn("Modules:" + name + ":Database", (
                    module / f"Acme.Commerce.{name}.Infrastructure/Persistence/DatabaseOptions.cs").read_text())
                api = module / f"Acme.Commerce.{name}.API/Acme.Commerce.{name}.API.csproj"
                self.run_cli("add", str(host / "Acme.Commerce.API.csproj"), "reference", str(api))
                program = host / "Program.cs"
                source = program.read_text()
                source = f"using Acme.Commerce.{name}.API;\n" + source
                source = source.replace("var app = builder.Build();", f"builder.Services.Add{name}Module(builder.Configuration);\nvar app = builder.Build();")
                source = source.replace("await app.RunAsync();", f"app.Map{name}Endpoints();\nawait app.RunAsync();")
                program.write_text(source)
                projects = [str(p) for p in module.rglob("*.csproj")]
                self.run_cli("sln", str(system / "Commerce.slnx"), "add", *projects)
                self.run_cli("build", str(system / "Commerce.slnx"), "--warnaserror")
                for kind in ("IntegrationTests", "ArchitectureTests"):
                    self.run_cli("test", str(module / f"tests/Acme.Commerce.{name}.{kind}"), "--no-build")
                # Each invocation preserves the existing host and selection record;
                # only the manual reference and hook edits above integrate modules.
                self.assertEqual(before[record], record.read_bytes())
            listing = self.run_cli("sln", str(system / "Commerce.slnx"), "list")
            self.assertIn("Acme.Commerce.Orders.API.csproj", listing)
            self.assertIn("Acme.Commerce.Billing.API.csproj", listing)

    @unittest.skipUnless(os.environ.get("ARCH_TEST_CONTAINERS") == "1", "Set ARCH_TEST_CONTAINERS=1 for real module databases")
    def test_two_modules_serve_owned_queries_through_the_integrated_public_host(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                         "--composition", "modular-monolith", "--output", str(system))
            boundary = system / "src/Commerce"
            host = boundary / "Acme.Commerce.API"
            env = dict(self.env)
            compose = ["docker", "compose", "--project-name", "arch-modules-" + Path(fixture).name.lower()]
            modules = []
            for name in ("Orders", "Billing"):
                module = boundary / "Modules" / name
                modules.append((name, module))
                self.run_cli("new", "arch-module", "--name", name, "--rootNamespace", "Acme.Commerce",
                             "--domainModel", "anemic", "--applicationFlow", "direct-service",
                             "--database", "postgresql", "--output", str(module))
                # Catalog-only capability fixture, never included in the package.
                for layer in ("Application", "Domain", "Infrastructure", "Contract"):
                    source = REPO / f"tests/fixtures/direct-service/Acme.Orders.{layer}"
                    target = module / f"Acme.Commerce.{name}.{layer}"
                    for path in source.rglob("*.cs"):
                        destination = target / path.relative_to(source)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_text(path.read_text().replace("Acme.Orders", f"Acme.Commerce.{name}")
                                               .replace("OrdersDbContext", f"{name}DbContext")
                                               .replace('"Orders".', f'"{name}".'))
                fixture_api = (REPO / "tests/fixtures/modular-monolith/ReservationEndpoint.cs").read_text()
                fixture_api = fixture_api.replace("CatalogModule", name)
                (module / f"Acme.Commerce.{name}.API/Reservations.cs").write_text(fixture_api)
                registration = module / f"Acme.Commerce.{name}.API/ModuleRegistration.cs"
                source = registration.read_text()
                source = source.replace(f"services.Add{name}Persistence(configuration);", f"services.Add{name}Persistence(configuration);\n        Reservations.Register(services);")
                source = source.replace("return endpoints;", "Reservations.Map(endpoints);\n        return endpoints;")
                registration.write_text(source)
                self.run_cli("add", str(host / "Acme.Commerce.API.csproj"), "reference",
                             str(module / f"Acme.Commerce.{name}.API/Acme.Commerce.{name}.API.csproj"))
                program = host / "Program.cs"
                source = f"using Acme.Commerce.{name}.API;\n" + program.read_text()
                source = source.replace("var app = builder.Build();", f"builder.Services.Add{name}Module(builder.Configuration);\nvar app = builder.Build();")
                source = source.replace("await app.RunAsync();", f"app.Map{name}Endpoints();\nawait app.RunAsync();")
                program.write_text(source)
                self.run_cli("sln", str(system / "Commerce.slnx"), "add", *[str(p) for p in module.rglob("*.csproj")])
                env[f"{name}_POSTGRES_PASSWORD"] = secrets.token_hex(16)
                override = module / "compose.fixture.yaml"
                override.write_text(f'services:\n  {name}-database:\n    ports: ["127.0.0.1::5432"]\n')
                compose.extend(["--file", str(module / "compose.postgresql.yaml"), "--file", str(override)])
            integration = boundary / "tests/Acme.Commerce.IntegrationTests"
            shutil.copy(REPO / "tests/fixtures/modular-monolith/ModuleUseCaseTests.cs", integration)

            def command(args, cwd=system, timeout=120):
                result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                for name, _ in modules:
                    self.assertNotIn(env[f"{name}_POSTGRES_PASSWORD"], result.stdout + result.stderr)
                return result.stdout

            self.run_cli("build", str(system / "Commerce.slnx"), "--warnaserror")
            try:
                command([*compose, "up", "--detach", "--wait", "--wait-timeout", "90"], timeout=180)
                for name, module in modules:
                    port = command([*compose, "port", f"{name}-database", "5432"]).strip().rsplit(":", 1)[1]
                    env[f"Modules__{name}__Database__ConnectionString"] = (
                        f"Host=127.0.0.1;Port={port};Database={name};Username={name};Password={env[f'{name}_POSTGRES_PASSWORD']};Timeout=5")
                    command(["dotnet", "tool", "restore"], cwd=module)
                    migration = ["--project", f"Acme.Commerce.{name}.Infrastructure", "--context", f"{name}DbContext"]
                    command(["dotnet", "ef", "migrations", "add", "Initial", *migration,
                             "--output-dir", "Persistence/Migrations/PostgreSql"], cwd=module)
                    command(["dotnet", "ef", "database", "update", *migration], cwd=module)
                output = command(["dotnet", "test", str(integration)])
                self.assertIn("Passed!", output)
                for name, _ in modules:
                    count = command([*compose, "exec", "-T", f"{name}-database", "psql", "-U", name, "-d", name,
                                     "-Atc", f'SELECT count(*) FROM "{name}"."Reservations";']).strip()
                    self.assertEqual("1", count)
                    other = "Billing" if name == "Orders" else "Orders"
                    self.assertEqual("t", command([*compose, "exec", "-T", f"{name}-database", "psql", "-U", name, "-d", name,
                                                   "-Atc", f"SELECT to_regclass('\"{other}\".\"Reservations\"') IS NULL;"]).strip())
            finally:
                command([*compose, "down", "--volumes", "--remove-orphans"])

    def test_documented_module_preflight_refuses_unsafe_targets_and_inputs(self):
        guide = (REPO / "docs/catalog/modular-monolith.md").read_text()
        preflight, = [block for block in re.findall(r"```bash\n(.*?)```", guide, re.S)
                      if "module_name=Orders" in block]
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                         "--composition", "modular-monolith", "--output", str(system))
            boundary = system / "src/Commerce"
            destination = boundary / "Modules/Orders"
            cases = [("module_name=Orders", "module_name=bad-name"),
                     ("root_namespace=Acme.Commerce", "root_namespace=Acme.bad-name"),
                     ("domain_model=anemic", "domain_model=rich"),
                     ("application_flow=direct-service", "application_flow=cqrs"),
                     ("database=postgresql", "database=unknown"),
                     ('intended_solution="$PWD/Commerce.slnx"', 'intended_solution="$PWD/missing.slnx"'),
                     ('host_boundary="$PWD/src/Commerce"', 'host_boundary="$PWD/src/Missing"')]
            before = {p: p.read_bytes() for p in system.rglob("*") if p.is_file()}
            for valid, invalid in cases:
                result = subprocess.run(["bash", "-c", preflight.replace(valid, invalid)], cwd=system,
                                        env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode, invalid)
                self.assertFalse(destination.exists())
                self.assertEqual(before, {p: p.read_bytes() for p in before})
            # A flat host requires explicit conversion, even if the output folder is fresh.
            flat = boundary / "Acme.Commerce.Application"
            flat.mkdir()
            result = subprocess.run(["bash", "-c", preflight], cwd=system, env=self.env, capture_output=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
            self.assertIn(b"conversion", result.stderr)
            self.assertFalse(destination.exists())
            flat.rmdir()
            destination.mkdir(parents=True)
            for kind in ("empty", "nonempty", "symlink"):
                if kind == "nonempty":
                    (destination / "keep.txt").write_text("preserve")
                elif kind == "symlink":
                    (destination / "keep.txt").unlink()
                    destination.rmdir()
                    destination.symlink_to(system / "missing", target_is_directory=True)
                result = subprocess.run(["bash", "-c", preflight], cwd=system, env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode)
                if kind == "nonempty":
                    self.assertEqual("preserve", (destination / "keep.txt").read_text())
            destination.unlink()
            collision = system / "other/Acme.Commerce.Orders.Contract.csproj"
            collision.parent.mkdir()
            collision.write_text("<Project />")
            result = subprocess.run(["bash", "-c", preflight], cwd=system, env=self.env, capture_output=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(destination.exists())
            collision.unlink()
            result = subprocess.run(["bash", "-c", preflight], cwd=system, env=self.env, capture_output=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((destination / "Acme.Commerce.Orders.API/ModuleRegistration.cs").exists())
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_native_module_generation_preserves_adjacent_nested_missing_and_ambiguous_solutions(self):
        for scenario in ("missing", "ancestor", "adjacent", "nested", "ambiguous"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory(dir=self.root) as fixture:
                root = Path(fixture)
                cwd = root / "work"
                cwd.mkdir()
                if scenario != "missing":
                    (root / "Ancestor.slnx").write_text("<Solution />\n")
                if scenario in ("adjacent", "ambiguous"):
                    (cwd / "First.slnx").write_text("<Solution />\n")
                if scenario == "ambiguous":
                    (cwd / "Second.slnx").write_text("<Solution />\n")
                if scenario == "nested":
                    (cwd / "nested").mkdir()
                    (cwd / "nested/Unrelated.slnx").write_text("<Solution />\n")
                (cwd / "Program.cs").write_text("// unrelated host\n")
                (cwd / "architecture.json").write_text("{}\n")
                before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.run_cli("new", "arch-module", "--name", "Orders", "--rootNamespace", "Acme.Commerce",
                             "--domainModel", "anemic", "--applicationFlow", "direct-service", "--database", "postgresql",
                             "--output", str(cwd / "Modules/Orders"), cwd=cwd)
                self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_native_module_missing_or_unsupported_selections_leave_no_files(self):
        cases = [[], ["--domainModel", "anemic", "--applicationFlow", "cqrs", "--database", "postgresql"],
                 ["--domainModel", "rich", "--applicationFlow", "direct-service", "--database", "postgresql"],
                 ["--domainModel", "anemic", "--applicationFlow", "direct-service", "--database", "unknown"]]
        for selections in cases:
            with self.subTest(selections=selections), tempfile.TemporaryDirectory(dir=self.root) as fixture:
                destination = Path(fixture) / "Orders"
                result = subprocess.run(["dotnet", "new", "arch-module", "--name", "Orders", "--rootNamespace", "Acme.Commerce",
                                         "--output", str(destination), *selections], env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual([], list(destination.rglob("*")))
