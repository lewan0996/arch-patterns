using Acme.Orders.Application.Reservations;
using Acme.Orders.Contract.Reservations;
using Acme.Orders.Domain.Reservations;
using Acme.Orders.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Acme.Orders.Infrastructure.Reservations;

public sealed class ReservationMapping : IEntityTypeConfiguration<Reservation>
{
    public void Configure(EntityTypeBuilder<Reservation> entity)
    {
        entity.ToTable("Reservations");
        entity.HasKey(reservation => reservation.Id);
        entity.Property(reservation => reservation.Reference).HasMaxLength(200).IsRequired();
        entity.HasIndex(reservation => reservation.Reference).IsUnique();
    }
}

public sealed class ReservationStore(OrdersDbContext database) : IReservationStore
{
    public async Task SaveAsync(Reservation reservation, CancellationToken cancellationToken)
    {
        database.Set<Reservation>().Add(reservation);
        await database.SaveChangesAsync(cancellationToken);
    }
}

public sealed class ReservationQueries(OrdersDbContext database) : IReservationQueries
{
    public Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken) =>
        database.Database.SqlQuery<ReservationDetails>($"""
            SELECT "Id", "Reference", "Seats" FROM "Orders"."Reservations"
            WHERE "Reference" = {reference}
            """).SingleOrDefaultAsync(cancellationToken);
}
