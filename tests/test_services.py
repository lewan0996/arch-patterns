"""Verify the installed service template through its documented creation chain."""

from pathlib import Path
import concurrent.futures
import json
import os
import re
import secrets
import signal
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import unittest

from test_templates import InstalledPackage, REPO


class ServiceTemplates(InstalledPackage):
    def generate(self, destination, name="Orders", namespace="Acme"):
        self.run_cli("new", "arch-service", "--name", name, "--rootNamespace", namespace,
                     "--domainModel", "anemic", "--applicationFlow", "direct-service",
                     "--database", "postgresql", "--output", str(destination))

    def test_flat_service_builds_and_runs_its_boundary_owned_checks(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            root = Path(fixture)
            self.run_cli("new", "arch-solution", "--name", "Commerce",
                         "--rootNamespace", "Acme", "--composition", "microservices",
                         "--output", str(root / "Commerce"))
            system = root / "Commerce"
            service = system / "src/Orders"
            self.run_cli("new", "arch-service", "--name", "Orders", "--rootNamespace", "Acme",
                         "--domainModel", "anemic", "--applicationFlow", "direct-service",
                         "--database", "postgresql", "--output", str(service), cwd=system)
            projects = sorted(service.rglob("*.csproj"))
            self.assertEqual(8, len(projects))
            self.assertFalse((service / "Modules").exists())
            self.assertEqual([], list(service.rglob("obj")))
            self.run_cli("sln", "Commerce.slnx", "add", *map(str, projects), cwd=system)
            self.run_cli("restore", "Commerce.slnx", cwd=system)
            self.run_cli("build", "Commerce.slnx", "--no-restore", "--warnaserror", cwd=system)
            for kind in ("Integration", "Architecture"):
                output = self.run_cli("test", str(service / "tests" / f"Acme.Orders.{kind}Tests"),
                                      "--no-build", cwd=system)
                self.assertIn("Passed!", output)
            # Prove the generated guard detects a forbidden dependency, rather than
            # passing only because the stock scaffold is empty.
            contract = service / "Acme.Orders.Contract/Acme.Orders.Contract.csproj"
            contract.write_text(contract.read_text().replace("</Project>", '''<ItemGroup>
<ProjectReference Include="../Acme.Orders.API/Acme.Orders.API.csproj" />
</ItemGroup></Project>'''))
            rejected = subprocess.run(["dotnet", "test", str(service / "tests/Acme.Orders.ArchitectureTests"),
                                       "--no-build"], env=self.env, cwd=system, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("Failed", rejected.stdout)

    def test_service_generation_preserves_every_existing_solution_until_explicit_manual_add(self):
        for solutions in ((), ("Commerce.slnx",), ("Commerce.slnx", "Other.slnx"),
                          ("Commerce.slnx", "src/Nested.slnx"), ("adjacent/Other.slnx",)):
            with self.subTest(solutions=solutions), tempfile.TemporaryDirectory(dir=self.root) as fixture:
                root = Path(fixture)
                for name in solutions:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("<Solution />\n")
                (root / "keep.txt").write_text("preserve me\n")
                before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
                destination = root / "src/Billing"
                self.generate(destination, "Billing", "Example.Commerce")
                after = {p: p.read_bytes() for p in root.rglob("*")
                         if p.is_file() and not p.is_relative_to(destination)}
                self.assertEqual(before, after)
                self.assertTrue((destination / "Example.Commerce.Billing.API/Program.cs").is_file())

    def test_host_propagates_request_budget_and_sigterm_cancellation(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.generate(service)
            api = service / "Acme.Orders.API"
            # Catalog-only endpoints exercise real middleware without adding business samples
            # to the production template. Both test paths use the same generated host.
            program = api / "Program.cs"
            program.write_text(program.read_text().replace("await app.RunAsync();", '''
app.MapGet("/fixture/wait", async (CancellationToken cancellation) =>
    await Task.Delay(Timeout.Infinite, cancellation));
await app.RunAsync();'''))
            self.run_cli("build", str(api), "--warnaserror")
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            address = f"http://127.0.0.1:{port}"
            env = dict(self.env, Service__Deployment="fixture", Service__RequestTimeoutSeconds="1",
                       Database__ConnectionString="Host=127.0.0.1;Port=1;Database=fixture;Username=fixture;Password=fixture",
                       ASPNETCORE_URLS=address, Unused__Secret="do-not-log-this-fixture-secret")
            with tempfile.NamedTemporaryFile(mode="w+") as logs:
                process = subprocess.Popen(["dotnet", str(api / "bin/Debug/net10.0/Acme.Orders.API.dll")],
                                           env=env, cwd=api, stdout=logs, stderr=subprocess.STDOUT)
                try:
                    self.wait_ready(address, process, path="/health/live")
                    with self.assertRaises(urllib.error.HTTPError) as timeout:
                        urllib.request.urlopen(address + "/fixture/wait", timeout=5)
                    self.assertEqual(504, timeout.exception.code)
                    timeout.exception.close()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        def request():
                            try:
                                return urllib.request.urlopen(address + "/fixture/wait", timeout=5).status
                            except urllib.error.HTTPError as error:
                                code = error.code
                                error.close()
                                return code
                        pending = executor.submit(request)
                        # Observe the framework's request-start log before delivering SIGTERM.
                        deadline = time.monotonic() + 5
                        while time.monotonic() < deadline:
                            if Path(logs.name).read_text().count("Request starting HTTP/1.1 GET " + address + "/fixture/wait") >= 2:
                                break
                            time.sleep(.02)
                        else:
                            self.fail("Second request did not reach the host")
                        process.send_signal(signal.SIGTERM)
                        self.assertEqual(503, pending.result(timeout=5))
                    self.assertEqual(0, process.wait(timeout=5))
                    output = Path(logs.name).read_text()
                    self.assertNotIn(env["Unused__Secret"], output)
                    records = [json.loads(line) for line in output.splitlines()]
                    self.assertTrue(any("shutting down" in r.get("Message", "") for r in records))
                    self.assertTrue(any(r.get("State", {}).get("Deployment") == "fixture" for r in records))
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()

    def test_documented_preflight_refuses_occupied_invalid_unsupported_and_duplicate_inputs(self):
        guide = (REPO / "docs/catalog/flat-service.md").read_text()
        preflight, = [block for block in re.findall(r"```bash\n(.*?)```", guide, re.S)
                      if "service_name=Orders" in block]
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            system = Path(fixture)
            solution = system / "Commerce.slnx"
            solution.write_text("<Solution />\n")
            destination = system / "src/Orders"
            destination.parent.mkdir()
            cases = [("service_name=Orders", "service_name=bad-name"),
                     ("root_namespace=Acme", "root_namespace=Acme.bad-name"),
                     ("layout=single", "layout=modular"),
                     ("domain_model=anemic", "domain_model=rich"),
                     ("application_flow=direct-service", "application_flow=cqrs"),
                     ("database=postgresql", "database=sql-server"),
                     ('intended_solution="$PWD/Commerce.slnx"', 'intended_solution="$PWD/missing.slnx"')]
            for valid, invalid in cases:
                result = subprocess.run(["bash", "-c", preflight.replace(valid, invalid)],
                                        cwd=system, env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(destination.exists())
            destination.mkdir()
            for existing in ("empty", "nonempty", "symlink"):
                if existing == "nonempty":
                    (destination / "keep.txt").write_text("preserve\n")
                elif existing == "symlink":
                    (destination / "keep.txt").unlink()
                    destination.rmdir()
                    destination.symlink_to(system / "missing", target_is_directory=True)
                result = subprocess.run(["bash", "-c", preflight], cwd=system,
                                        env=self.env, capture_output=True, timeout=30)
                self.assertNotEqual(0, result.returncode)
                if existing == "nonempty":
                    self.assertEqual("preserve\n", (destination / "keep.txt").read_text())
            destination.unlink()
            collision = system / "src/Existing/Acme.Orders.API.csproj"
            collision.parent.mkdir()
            collision.write_text("<Project />")
            result = subprocess.run(["bash", "-c", preflight], cwd=system,
                                    env=self.env, capture_output=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(destination.exists())
            collision.unlink()
            result = subprocess.run(["bash", "-c", preflight], cwd=system,
                                    env=self.env, capture_output=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((destination / "Acme.Orders.API/Program.cs").exists())
            self.assertEqual("<Solution />\n", solution.read_text())

    @unittest.skipUnless(os.environ.get("ARCH_TEST_CONTAINERS") == "1", "Set ARCH_TEST_CONTAINERS=1 for OCI checks")
    def test_portable_image_requires_configuration_and_handles_sigterm(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            service = Path(fixture) / "Orders"
            self.generate(service)
            tag = "arch-service-" + Path(fixture).name.lower()
            secret = secrets.token_hex(16)
            env = dict(self.env, POSTGRES_PASSWORD=secret)
            compose = ("compose", "--project-name", tag, "--file", str(service / "compose.postgresql.yaml"))
            containers = []
            def docker(*args, check=True):
                result = subprocess.run(["docker", *args], env=env, capture_output=True, text=True, timeout=240)
                if check:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                return (result.stdout + (result.stderr if args[0] == "logs" else "")).strip()
            try:
                docker("build", "--tag", tag, str(service))
                invalid = docker("run", "--detach", tag)
                containers.append(invalid)
                self.assertNotEqual("0", docker("wait", invalid))
                self.assertIn("Deployment", docker("logs", invalid))
                invalid_database = docker("run", "--detach", "--env", "Service__Deployment=container", tag)
                containers.append(invalid_database)
                self.assertNotEqual("0", docker("wait", invalid_database))
                self.assertIn("Database:ConnectionString", docker("logs", invalid_database))
                docker(*compose, "up", "--detach", "--wait")
                env["Database__ConnectionString"] = f"Host=database;Database=Orders;Username=Orders;Password={secret};Timeout=5"
                valid = docker("run", "--detach", "--network", tag + "_default", "--publish", "127.0.0.1::8080",
                               "--env", "Service__Deployment=container",
                               "--env", "Database__ConnectionString", tag)
                containers.append(valid)
                port = docker("inspect", "--format", '{{(index (index .NetworkSettings.Ports "8080/tcp") 0).HostPort}}', valid)
                self.wait_ready("http://127.0.0.1:" + port)
                self.assertNotEqual("0", docker("inspect", "--format", "{{.Config.User}}", valid))
                docker("stop", "--time", "20", valid)
                self.assertEqual("0", docker("inspect", "--format", "{{.State.ExitCode}}", valid))
            finally:
                for container in containers:
                    docker("rm", "--force", container, check=False)
                docker(*compose, "down", "--volumes", "--remove-orphans", check=False)
                docker("image", "rm", tag, check=False)

    @staticmethod
    def wait_ready(address, process=None, path="/health/ready"):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process is not None and process.poll() is not None:
                raise AssertionError("Host exited before readiness")
            try:
                with urllib.request.urlopen(address + path, timeout=1) as response:
                    if response.status == 200:
                        return
            except urllib.error.HTTPError as error:
                error.close()
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(.05)
        raise AssertionError("Host did not become ready")
