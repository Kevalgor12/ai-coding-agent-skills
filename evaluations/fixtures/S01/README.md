# S01 Fixture — PostgreSQL duplicate-rows query bug

This is an isolated test fixture for evaluation scenario S01.

**Stack:** Node.js + Express + `pg` (raw SQL, no ORM) backend; React 18 SPA frontend.

**Bug location:** `backend/src/repositories/ordersRepository.js`

The `getOrdersByCustomerId` query fans out rows via an unaggregated JOIN on
`order_items` — a 3-item order returns 3 identical rows. The fix must deduplicate
using `GROUP BY` aggregation and include an `item_count` per order.
