namespace Acme.Orders.Domain.Reservations;

public sealed class Reservation
{
    private readonly List<ReservationSeatsChanged> domainEvents = [];

    private Reservation() { }

    public Guid Id { get; private set; }
    public string Reference { get; private set; } = "";
    public int Seats { get; private set; }
    public IReadOnlyList<ReservationSeatsChanged> DomainEvents => domainEvents.AsReadOnly();

    public static Reservation Create(string reference, int seats)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(reference);
        ValidateSeats(seats);
        return new() { Id = Guid.NewGuid(), Reference = reference, Seats = seats };
    }

    public void ChangeSeats(int seats)
    {
        ValidateSeats(seats);
        Seats = seats;
        domainEvents.Add(new ReservationSeatsChanged(Id, seats));
    }

    private static void ValidateSeats(int seats)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(seats, 1);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(seats, 8);
    }
}

public sealed record ReservationSeatsChanged(Guid ReservationId, int Seats);
