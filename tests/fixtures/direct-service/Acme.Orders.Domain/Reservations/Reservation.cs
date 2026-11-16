namespace Acme.Orders.Domain.Reservations;

public sealed class Reservation
{
    public Guid Id { get; set; }
    public string Reference { get; set; } = "";
    public int Seats { get; set; }
}
