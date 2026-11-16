using Acme.Orders.Domain.Reservations;

namespace Acme.Orders.Domain.UnitTests.Reservations;

public sealed class ReservationTests
{
    [Fact]
    public void Seat_changes_belong_to_the_aggregate_and_raise_a_module_owned_domain_event()
    {
        var reservation = Reservation.Create("domain", 2);
        reservation.ChangeSeats(4);
        Assert.Equal(4, reservation.Seats);
        Assert.Equal(new ReservationSeatsChanged(reservation.Id, 4), Assert.Single(reservation.DomainEvents));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(9)]
    public void Invalid_seat_counts_leave_existing_state_and_domain_events_unchanged(int seats)
    {
        var reservation = Reservation.Create("unchanged", 2);
        Assert.Throws<ArgumentOutOfRangeException>(() => reservation.ChangeSeats(seats));
        Assert.Equal(2, reservation.Seats);
        Assert.Empty(reservation.DomainEvents);
        Assert.Throws<ArgumentOutOfRangeException>(() => Reservation.Create("invalid", seats));
    }

    [Fact]
    public void Blank_reference_cannot_create_a_reservation() =>
        Assert.Throws<ArgumentException>(() => Reservation.Create(" ", 2));
}
