"""Exercise the installed package through the public dotnet CLI."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class InstalledPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix="arch-templates-")
        cls.root = Path(cls.fixture.name)
        cls.env = dict(os.environ, DOTNET_CLI_HOME=str(cls.root / "cli-home"),
                       DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
                       DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1",
                       DOTNET_CLI_UI_LANGUAGE="en-US")
        try:
            cls.run_cli("pack", str(REPO / "templates/ArchPatterns.Templates.csproj"),
                        "--configuration", "Release", "--output", str(cls.root / "packages"))
            package, = (cls.root / "packages").glob("*.nupkg")
            cls.run_cli("new", "install", str(package))
        except Exception:
            cls.fixture.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    @classmethod
    def run_cli(cls, *args, cwd=REPO):
        result = subprocess.run(["dotnet", *args], cwd=cwd, env=cls.env,
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=120)
        if result.returncode:
            raise AssertionError(f"dotnet {' '.join(args)}\n{result.stdout}")
        return result.stdout


class InstalledTemplates(InstalledPackage):
    def test_installed_package_is_discoverable_with_required_inputs_in_help(self):
        listing = self.run_cli("new", "list", "arch-")
        self.assertIn("arch-solution", listing)
        self.assertIn("arch-service", listing)
        self.assertIn("arch-module", listing)
        for future_entry in ("arch-bff", "arch-audience-api"):
            self.assertNotIn(future_entry, listing)
        help_text = self.run_cli("new", "arch-solution", "--help")
        for option in ("--composition", "microservices", "--rootNamespace"):
            self.assertIn(option, help_text)
        service_help = self.run_cli("new", "arch-service", "--help")
        for option in ("--rootNamespace", "--layout", "--domainModel", "--applicationFlow", "--database"):
            self.assertIn(option, service_help)

    def test_microservices_workspace_has_toolchain_and_no_system_host(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            parent = Path(fixture)
            # Nearby solutions and source must remain byte-for-byte intact.
            (parent / "Existing.slnx").write_text("<Solution />\n")
            (parent / "Program.cs").write_text("// existing source\n")
            before = {p: p.read_bytes() for p in parent.iterdir()}
            destination = parent / "commerce workspace"
            self.run_cli("new", "arch-solution", "--name", "Commerce",
                         "--rootNamespace", "Acme.Commerce", "--composition", "microservices",
                         "--output", str(destination), cwd=parent)
            self.assertTrue((destination / "Commerce.slnx").is_file())
            self.assertEqual([], list(destination.rglob("*.csproj")))
            self.assertEqual([], list(destination.rglob("*.cs")))
            self.assertEqual([], list(destination.rglob("obj")))
            sdk = json.loads((destination / "global.json").read_text())["sdk"]
            self.assertEqual("10.0.401", sdk["version"])
            self.assertEqual("disable", sdk["rollForward"])
            devcontainer = json.loads((destination / ".devcontainer/devcontainer.json").read_text())
            self.assertEqual("workspace", devcontainer["service"])
            self.assertTrue((destination / ".devcontainer" / devcontainer["dockerComposeFile"]).is_file())
            instructions = (destination / "README.md").read_text()
            for required in ("Commerce", "Acme.Commerce", "microservices", "dotnet restore Commerce.slnx",
                             "dotnet build Commerce.slnx --no-restore", "secret", "Compose"):
                self.assertIn(required, instructions)
            self.assertNotIn("CatalogSystem", instructions)
            self.assertNotIn("CatalogNamespace", instructions)
            self.run_cli("sln", "Commerce.slnx", "list", cwd=destination)
            self.run_cli("restore", "Commerce.slnx", cwd=destination)
            self.run_cli("build", "Commerce.slnx", "--no-restore", cwd=destination)
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_missing_or_unsupported_native_inputs_fail_without_output(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            parent = Path(fixture)
            cases = (
                (["--rootNamespace", "Acme"], "composition"),
                (["--composition", "microservices"], "rootNamespace"),

                (["--rootNamespace", "Acme", "--composition", "unknown"], "composition"),
            )
            for index, (inputs, diagnostic) in enumerate(cases):
                with self.subTest(inputs=inputs):
                    destination = parent / str(index)
                    result = subprocess.run(
                        ["dotnet", "new", "arch-solution", "--name", "Commerce",
                         "--output", str(destination), *inputs],
                        env=self.env, cwd=parent, text=True, capture_output=True, timeout=30)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn(diagnostic, result.stdout + result.stderr)
                    # SDK 10 may create an empty destination before required-input validation.
                    self.assertEqual([], list(destination.rglob("*")))

    def test_documented_preflight_rejects_collisions_and_invalid_identities(self):
        guide = (REPO / "docs/catalog/microservices-solution.md").read_text()
        preflight, = [block for block in re.findall(r"```bash\n(.*?)```", guide, re.S)
                      if "system_name=Commerce" in block]
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            parent = Path(fixture)
            destination = parent / "Commerce"
            destination.mkdir()
            for occupied in ("empty directory", "existing files", "dangling symlink"):
                with self.subTest(occupied=occupied):
                    if occupied == "existing files":
                        (destination / "keep.txt").write_bytes(b"preserve me\n")
                    elif occupied == "dangling symlink":
                        (destination / "keep.txt").unlink()
                        destination.rmdir()
                        destination.symlink_to(parent / "missing", target_is_directory=True)
                    result = subprocess.run(["bash", "-c", preflight], cwd=parent,
                                            env=self.env, capture_output=True, timeout=30)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn(b"Destination already exists", result.stderr)
                    if occupied == "existing files":
                        self.assertEqual(b"preserve me\n", (destination / "keep.txt").read_bytes())
                    self.assertEqual([destination], list(parent.iterdir()))
            destination.unlink()
            invalid_inputs = (("system_name=Commerce", "system_name=bad-name"),
                              ("root_namespace=Acme.Commerce", "root_namespace=Acme.bad-name"))
            for valid, invalid in invalid_inputs:
                with self.subTest(invalid=invalid):
                    script = preflight.replace(valid, invalid)
                    result = subprocess.run(["bash", "-c", script], cwd=parent,
                                            env=self.env, capture_output=True, timeout=30)
                    self.assertNotEqual(0, result.returncode)
                    self.assertEqual([], list(parent.iterdir()))
            # The exact published successful path also runs through the installed package.
            subprocess.run(["bash", "-c", preflight], cwd=parent, env=self.env,
                           check=True, capture_output=True, timeout=30)
            self.assertTrue((destination / "Commerce.slnx").is_file())

    def test_generation_preserves_no_ancestor_nested_and_ambiguous_solutions(self):
        cases = ((), ("Existing.slnx",), ("Existing.slnx", "Other.slnx"),
                 ("nested/Existing.slnx", "Existing.slnx"))
        for solutions in cases:
            with self.subTest(solutions=solutions), tempfile.TemporaryDirectory(dir=self.root) as fixture:
                parent = Path(fixture)
                (parent / "keep.txt").write_text("untouched\n")
                for solution in solutions:
                    path = parent / solution
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("<Solution />\n")
                before = {p: p.read_bytes() for p in parent.rglob("*") if p.is_file()}
                destination = parent / "nested" / "new-system"
                self.run_cli("new", "arch-solution", "--name", "Billing",
                             "--rootNamespace", "Example.Platform", "--composition", "microservices",
                             "--output", str(destination), cwd=parent)
                after = {p: p.read_bytes() for p in parent.rglob("*")
                         if p.is_file() and not p.is_relative_to(destination)}
                self.assertEqual(before, after)
                self.assertTrue((destination / "Billing.slnx").is_file())
                self.assertTrue((destination / ".gitignore").is_file())

    @unittest.skipUnless(os.environ.get("ARCH_TEST_CONTAINERS") == "1",
                         "Set ARCH_TEST_CONTAINERS=1 to exercise the generated Dev Container toolchain")
    def test_generated_compose_toolchain_runs_the_pinned_sdk_and_solution_checks(self):
        with tempfile.TemporaryDirectory(dir=self.root) as fixture:
            destination = Path(fixture) / "Commerce"
            self.run_cli("new", "arch-solution", "--name", "Commerce",
                         "--rootNamespace", "Acme.Commerce", "--composition", "microservices",
                         "--output", str(destination))
            compose = ["docker", "compose", "--project-name", "arch-" + Path(fixture).name,
                       "--file", str(destination / ".devcontainer/compose.yaml")]

            def run(*args):
                result = subprocess.run([*compose, *args], text=True, capture_output=True, timeout=240)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                return result.stdout

            try:
                run("config", "--quiet")
                run("up", "--detach", "--wait")
                self.assertEqual("10.0.401", run("exec", "-T", "workspace", "dotnet", "--version").strip())
                run("exec", "-T", "workspace", "dotnet", "restore", "Commerce.slnx")
                run("exec", "-T", "workspace", "dotnet", "build", "Commerce.slnx", "--no-restore")
            finally:
                run("down", "--volumes", "--remove-orphans")


if __name__ == "__main__":
    unittest.main()
