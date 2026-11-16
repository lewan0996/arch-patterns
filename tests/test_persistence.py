"""Public direct-service behavior against the generated PostgreSQL composition."""

from pathlib import Path
import os
import secrets
import shutil
import subprocess
import tempfile
import unittest

from test_templates import InstalledPackage, REPO


class PersistenceTemplates(InstalledPackage):
    def test_explicit_anemic_direct_service_postgresql_profile_builds(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "anemic", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service))
            self.run_cli("build", str(service / "Acme.Orders.API"), "--warnaserror")

    def test_missing_and_unsupported_profiles_fail_without_files(self):
        cases = [[], ["--domainModel", "rich", "--applicationFlow", "direct-service", "--database", "postgresql"],
                 ["--domainModel", "anemic", "--applicationFlow", "cqrs", "--database", "postgresql"],
                 ["--domainModel", "anemic", "--applicationFlow", "direct-service", "--database", "sql-server"]]
        for args in cases:
            with self.subTest(args=args), tempfile.TemporaryDirectory(dir=self.root) as fixture:
                destination = Path(fixture) / "Orders"
                result = subprocess.run(["dotnet", "new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                                         "--output", str(destination), *args], env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual([], list(destination.rglob("*")))

    @unittest.skipUnless(os.environ.get("ARCH_TEST_CONTAINERS") == "1", "Set ARCH_TEST_CONTAINERS=1 for real PostgreSQL")
    def test_direct_service_uses_real_postgresql_and_explicit_migrations(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce", "--rootNamespace", "Acme",
                         "--composition", "microservices", "--output", str(system))
            service = system / "src/Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "anemic", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service))
            shutil.copytree(REPO / "tests/fixtures/direct-service", service, dirs_exist_ok=True)
            # First prove the public use-case fixture compiles against the generated boundary.
            self.run_cli("build", str(service / "tests/Acme.Orders.IntegrationTests"), "--warnaserror")
            secret = secrets.token_hex(16)
            env = dict(self.env, POSTGRES_PASSWORD=secret)
            override = service / "compose.fixture.yaml"
            override.write_text('services:\n  database:\n    ports: ["127.0.0.1::5432"]\n')
            compose = ["docker", "compose", "--project-name", "arch-pg-" + Path(fixture).name.lower(),
                       "--file", str(system / ".devcontainer/compose.yaml"),
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
                migration_args = ["--project", "Acme.Orders.Infrastructure", "--context", "OrdersDbContext"]
                command(["dotnet", "ef", "migrations", "add", "FixtureInitial", *migration_args,
                         "--output-dir", "Persistence/Migrations/PostgreSql"])
                script = service / "migrations.sql"
                command(["dotnet", "ef", "migrations", "script", "--idempotent", *migration_args,
                         "--output", str(script)])
                self.assertIn('CREATE TABLE "Orders"."Reservations"', script.read_text())
                command(["dotnet", "ef", "database", "update", *migration_args])
                output = command(["dotnet", "test", "tests/Acme.Orders.IntegrationTests"])
                self.assertIn("Passed!", output)
                self.assertNotIn(secret, output)
                # Inspect committed data through PostgreSQL itself, independently of EF.
                persisted = command([*compose, "exec", "-T", "database", "psql", "-U", "Orders", "-d", "Orders",
                                     "-Atc", 'SELECT count(*) FROM "Orders"."Reservations";']).strip()
                self.assertEqual("1", persisted)
                # Exercise the documented merged Dev Container profile as well as host-side tests.
                exec_workspace = [*compose, "exec", "-T", "--user", f"{os.getuid()}:{os.getgid()}",
                                  "--env", "DOTNET_CLI_HOME=/tmp/arch-cli", "workspace"]
                command([*exec_workspace, "dotnet", "build", "src/Orders/Acme.Orders.API", "--warnaserror",
                         "--artifacts-path", "/tmp/arch-build"])
                original_connection = env["Database__ConnectionString"]
                env["Database__ConnectionString"] = f"Host=database;Database=Orders;Username=Orders;Password={secret};Timeout=5"
                command([*compose, "exec", "--detach", "--user", f"{os.getuid()}:{os.getgid()}",
                         "--env", "DOTNET_CLI_HOME=/tmp/arch-cli", "--env", "Database__ConnectionString",
                         "--env", "Service__Deployment=devcontainer", "--env", "ASPNETCORE_HTTP_PORTS=8080",
                         "workspace", "dotnet", "/tmp/arch-build/bin/Acme.Orders.API/debug/Acme.Orders.API.dll"])
                command([*exec_workspace, "curl", "--retry", "10", "--retry-connrefused", "--retry-delay", "1",
                         "--fail", "http://localhost:8080/health/ready"])
                env["Database__ConnectionString"] = original_connection
                command(["dotnet", "ef", "database", "update", "0", *migration_args])
                removed = command([*compose, "exec", "-T", "database", "psql", "-U", "Orders", "-d", "Orders",
                                   "-Atc", '''SELECT to_regclass('"Orders"."Reservations"') IS NULL;''']).strip()
                self.assertEqual("t", removed)
            finally:
                command([*compose, "down", "--volumes", "--remove-orphans"])
