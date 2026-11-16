using CatalogNamespace.CatalogSystem.API;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddJsonConsole();
builder.Services.AddOptions<ServiceOptions>()
    .Bind(builder.Configuration.GetSection(ServiceOptions.Section))
    .ValidateDataAnnotations().ValidateOnStart();
builder.Services.AddOptions<HostOptions>().Configure<IOptions<ServiceOptions>>((host, service) =>
    host.ShutdownTimeout = TimeSpan.FromSeconds(service.Value.ShutdownTimeoutSeconds));
builder.Services.AddHealthChecks().AddCheck<LifecycleHealthCheck>("lifecycle", tags: ["ready"]);

// Register each named module here, before builder.Build().

var app = builder.Build();
var settings = app.Services.GetRequiredService<IOptions<ServiceOptions>>().Value;
app.Logger.LogInformation("Starting {Service} in {Deployment}", "CatalogSystem", settings.Deployment);
app.Use(async (context, next) =>
{
    // Probes retain their own lifecycle semantics while business traffic drains.
    if (context.Request.Path.StartsWithSegments("/health"))
    {
        await next(context);
        return;
    }
    if (app.Lifetime.ApplicationStopping.IsCancellationRequested)
    {
        context.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
        return;
    }
    var clientCancellation = context.RequestAborted;
    using var budget = CancellationTokenSource.CreateLinkedTokenSource(
        clientCancellation, app.Lifetime.ApplicationStopping);
    budget.CancelAfter(TimeSpan.FromSeconds(settings.RequestTimeoutSeconds));
    context.RequestAborted = budget.Token;
    try
    {
        await next(context);
    }
    catch (OperationCanceledException) when (budget.IsCancellationRequested && !clientCancellation.IsCancellationRequested)
    {
        if (!context.Response.HasStarted)
            context.Response.StatusCode = app.Lifetime.ApplicationStopping.IsCancellationRequested
                ? StatusCodes.Status503ServiceUnavailable : StatusCodes.Status504GatewayTimeout;
        else
            context.Abort();
    }
    finally
    {
        context.RequestAborted = clientCancellation;
    }
});
app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
// Map each named module here, before app.RunAsync().
await app.RunAsync();

public partial class Program;
