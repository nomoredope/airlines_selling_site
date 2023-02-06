SELECT id_flight, tickets, price FROM airline.ordered WHERE order_date BETWEEN '$start_date' AND '$end_date'
JOIN airline.flights.price ON airline.flights.id_fl = airline.ordered.id_flight