INSERT INTO airline.ordered (id_user, id_flight, tickets, order_date, sum_price)
 VALUES ($id_user, '$id_flight', $tickets, NOW(), $tickets * $pr)