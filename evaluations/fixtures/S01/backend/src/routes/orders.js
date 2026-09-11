const express = require('express');
const router = express.Router();
const { getOrdersByCustomerId } = require('../repositories/ordersRepository');

router.get('/customers/:id/orders', async (req, res) => {
  try {
    const orders = await getOrdersByCustomerId(req.params.id);
    res.json(orders);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
