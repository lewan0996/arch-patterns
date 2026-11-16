"""Exercise the rich/direct-service selection through the installed package."""

from pathlib import Path
import os
import secrets
import shutil
import subprocess
import tempfile
import unittest

from test_templates import InstalledPackage, REPO


class RichDirectServiceTemplates(InstalledPackage):
    def test_rich_direct_service_is_explicit_and_preserves_the_five_project_boundary(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "rich", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service))
            self.assertEqual(8, len(list(service.rglob("*.csproj"))))
            self.assertEqual([], list(service.rglob("obj")))
            self.assertEqual([], list((service / "Acme.Orders.Domain").glob("*.cs")))
            guidance = (service / "Acme.Orders.Application/README.md").read_text()
            self.assertIn("rich", guidance)
            self.assertIn("aggregate-root repository", " ".join(guidance.split()))
            self.run_cli("build", str(service / "Acme.Orders.API"), "--warnaserror")
            output = self.run_cli("test", str(service / "tests/Acme.Orders.ArchitectureTests"))
            self.assertIn("Passed!", output)

    def test_rich_aggregate_owns_state_changes_and_domain_events(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "rich", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service))
            shutil.copytree(REPO / "tests/fixtures/rich-direct-service", service, dirs_exist_ok=True)
            output = self.run_cli("test", str(service / "tests/Acme.Orders.Domain.UnitTests"))
            self.assertIn("Passed!", output)

    def test_rich_cqrs_is_unverified_and_refused_without_files(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            destination = Path(fixture) / "Orders"
            result = subprocess.run(
                ["dotnet", "new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                 "--domainModel", "rich", "--applicationFlow", "cqrs", "--database", "postgresql",
                 "--output", str(destination)],
                env=self.env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], list(destination.rglob("*")))

    @unittest.skipUnless(os.environ.get("ARCH_TEST_CONTAINERS") == "1", "Set ARCH_TEST_CONTAINERS=1 for real PostgreSQL")
    def test_rich_direct_service_persists_aggregate_changes_and_queries_separate_shapes(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "rich", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service))
            shutil.copytree(REPO / "tests/fixtures/rich-direct-service", service, dirs_exist_ok=True)
            self.run_cli("build", str(service / "tests/Acme.Orders.IntegrationTests"), "--warnaserror")
            secret = secrets.token_hex(16)
            env = dict(self.env, POSTGRES_PASSWORD=secret)
            override = service / "compose.fixture.yaml"
            override.write_text('services:\n  database:\n    ports: ["127.0.0.1::5432"]\n')
            compose = ["docker", "compose", "--project-name", "arch-rich-" + Path(fixture).name.lower(),
                       "--file", str(service / "compose.postgresql.yaml"), "--file", str(override)]

            def command(args, timeout=120):
                result = subprocess.run(args, cwd=service, env=env, capture_output=True, text=True, timeout=timeout)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                return result.stdout

            try:
                command([*compose, "up", "--detach", "--wait", "--wait-timeout", "90"], timeout=180)
                port = command([*compose, "port", "database", "5432"]).strip().rsplit(":", 1)[1]
                env["Database__ConnectionString"] = (
                    f"Host=127.0.0.1;Port={port};Database=Orders;Username=Orders;Password={secret};Timeout=5")
                command(["dotnet", "tool", "restore"])
                migration = ["--project", "Acme.Orders.Infrastructure", "--context", "OrdersDbContext"]
                command(["dotnet", "ef", "migrations", "add", "RichFixtureInitial", *migration,
                         "--output-dir", "Persistence/Migrations/PostgreSql"])
                command(["dotnet", "ef", "database", "update", *migration])
                output = command(["dotnet", "test", "tests/Acme.Orders.IntegrationTests",
                                  "--filter", "FullyQualifiedName~RichDirectServiceUseCaseTests"])
                self.assertIn("Passed!", output)
                self.assertNotIn(secret, output)
                self.assertIn("Passed!", command(["dotnet", "test", "tests/Acme.Orders.ArchitectureTests"]))
            finally:
                command([*compose, "down", "--volumes", "--remove-orphans"])
