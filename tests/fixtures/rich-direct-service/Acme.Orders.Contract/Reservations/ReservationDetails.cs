namespace Acme.Orders.Contract.Reservations;

public sealed record ReservationDetails(Guid Id, string Reference, int Seats);
