const { pool } = require('../db');

/**
 * Returns all orders for a customer.
 * BUG: The JOIN on order_items fans out rows — a 3-item order returns 3 rows.
 */
async function getOrdersByCustomerId(customerId) {
  const result = await pool.query(
    `SELECT o.id, o.order_date, o.status, c.name AS customer_name
     FROM orders o
     JOIN customers c ON c.id = o.customer_id
     JOIN order_items oi ON oi.order_id = o.id
     WHERE c.id = $1
     ORDER BY o.order_date DESC`,
    [customerId]
  );
  return result.rows;
}

module.exports = { getOrdersByCustomerId };
