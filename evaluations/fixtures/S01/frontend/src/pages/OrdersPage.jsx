import React, { useEffect, useState } from 'react';

export default function OrdersPage({ customerId }) {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch(`/api/customers/${customerId}/orders`)
      .then(r => r.json())
      .then(setOrders);
  }, [customerId]);

  return (
    <ul>
      {orders.map(o => (
        <li key={o.id}>{o.order_date} — {o.status}</li>
      ))}
    </ul>
  );
}
