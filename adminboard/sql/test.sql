SELECT SUM(tickets), id_flight, SUM(sum_price) FROM airline.ordered WHERE order_date BETWEEN '$start_date' AND '$end_date'
GROUP BY id_flight
