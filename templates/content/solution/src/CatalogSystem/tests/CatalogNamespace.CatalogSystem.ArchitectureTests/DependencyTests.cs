using System.Xml.Linq;

namespace CatalogNamespace.CatalogSystem.ArchitectureTests;

public sealed class DependencyTests
{
    [Fact]
    public void Host_composes_only_its_named_module_API_projects()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !Directory.Exists(Path.Combine(root.FullName, "CatalogNamespace.CatalogSystem.API")))
            root = root.Parent;
        Assert.NotNull(root);
        var host = Path.Combine(root.FullName, "CatalogNamespace.CatalogSystem.API");
        var project = XDocument.Load(Path.Combine(host, "CatalogNamespace.CatalogSystem.API.csproj"));
        foreach (var reference in project.Descendants("ProjectReference"))
        {
            var path = Path.GetFullPath(Path.Combine(host, (string)reference.Attribute("Include")!));
            Assert.StartsWith(Path.Combine(root.FullName, "Modules") + Path.DirectorySeparatorChar, path);
            Assert.EndsWith(".API.csproj", path);
        }
    }
}
