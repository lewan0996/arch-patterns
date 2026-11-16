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
        entity.Ignore(reservation => reservation.DomainEvents);
    }
}

public sealed class ReservationRepository(OrdersDbContext database) : IReservationRepository
{
    public void Add(Reservation reservation) => database.Set<Reservation>().Add(reservation);

    public Task<Reservation?> LoadAsync(Guid id, CancellationToken cancellationToken) =>
        database.Set<Reservation>().SingleOrDefaultAsync(reservation => reservation.Id == id, cancellationToken);

    public Task SaveChangesAsync(CancellationToken cancellationToken) => database.SaveChangesAsync(cancellationToken);
}

public sealed class ReservationQueries(OrdersDbContext database) : IReservationQueries
{
    public Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken) =>
        database.Database.SqlQuery<ReservationDetails>($"""
            SELECT "Id", "Reference", "Seats" FROM "Orders"."Reservations"
            WHERE "Reference" = {reference}
            """).SingleOrDefaultAsync(cancellationToken);
}
