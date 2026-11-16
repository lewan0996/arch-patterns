using System.ComponentModel.DataAnnotations;

namespace CatalogNamespace.CatalogSystem.API;

public sealed class ServiceOptions
{
    public const string Section = "Service";

    [Required, MinLength(1)]
    public string Deployment { get; init; } = "";

    [Range(1, 300)]
    public int RequestTimeoutSeconds { get; init; } = 30;

    [Range(1, 300)]
    public int ShutdownTimeoutSeconds { get; init; } = 15;
}
