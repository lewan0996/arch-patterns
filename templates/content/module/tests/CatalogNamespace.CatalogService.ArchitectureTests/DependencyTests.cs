using System.Xml.Linq;

namespace CatalogNamespace.CatalogService.ArchitectureTests;

public sealed class DependencyTests
{
    [Fact]
    public void Production_projects_obey_inward_dependency_rules()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !Directory.Exists(Path.Combine(root.FullName, "CatalogNamespace.CatalogService.API")))
            root = root.Parent;
        Assert.NotNull(root);
        var allowed = new Dictionary<string, string[]>
        {
            ["API"] = ["Application", "Infrastructure", "Contract"],
            ["Application"] = ["Domain", "Contract"],
            ["Domain"] = [],
            ["Infrastructure"] = ["Application", "Domain"],
            ["Contract"] = []
        };
        foreach (var (layer, dependencies) in allowed)
        {
            var folder = Path.Combine(root.FullName, $"CatalogNamespace.CatalogService.{layer}");
            var document = XDocument.Load(Path.Combine(folder, $"CatalogNamespace.CatalogService.{layer}.csproj"));
            var permitted = dependencies.Select(name => Path.GetFullPath(Path.Combine(
                root.FullName, $"CatalogNamespace.CatalogService.{name}/CatalogNamespace.CatalogService.{name}.csproj"))).ToHashSet();
            foreach (var reference in document.Descendants("ProjectReference"))
                Assert.Contains(Path.GetFullPath(Path.Combine(folder, (string)reference.Attribute("Include")!)), permitted);
            if (layer is "Application" or "Domain" or "Contract")
            {
                Assert.Empty(document.Descendants("FrameworkReference"));
                foreach (var package in document.Descendants("PackageReference"))
                {
                    var name = (string)package.Attribute("Include")!;
                    Assert.False(name.StartsWith("Microsoft.EntityFrameworkCore", StringComparison.OrdinalIgnoreCase) ||
                                 name.StartsWith("Npgsql", StringComparison.OrdinalIgnoreCase) ||
                                 name.StartsWith("Wolverine", StringComparison.OrdinalIgnoreCase) ||
                                 name.Equals("Dapper", StringComparison.OrdinalIgnoreCase),
                        $"{layer} must not depend on Infrastructure tooling: {name}");
                }
            }
        }
    }
}
