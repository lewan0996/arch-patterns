using Npgsql;
using Microsoft.EntityFrameworkCore;

namespace CatalogNamespace.CatalogService.Infrastructure.Persistence;

public sealed class DatabaseOptions
{
    public const string Section = "Database";
    public string ConnectionString { get; init; } = "";

    internal void Configure(DbContextOptionsBuilder options) => options
        .UseNpgsql(ConnectionString, database => database
            .MigrationsHistoryTable("__EFMigrationsHistory", "CatalogService").CommandTimeout(10))
        .EnableSensitiveDataLogging(false);

    public bool IsValid()
    {
        try
        {
            var value = new NpgsqlConnectionStringBuilder(ConnectionString);
            return !string.IsNullOrWhiteSpace(value.Host) &&
                   !string.IsNullOrWhiteSpace(value.Database) &&
                   !string.IsNullOrWhiteSpace(value.Username) &&
                   !string.IsNullOrWhiteSpace(value.Password);
        }
        catch (ArgumentException)
        {
            return false;
        }
    }
}
