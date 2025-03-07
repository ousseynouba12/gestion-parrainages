const express = require('express');
const router = express.Router();
const db = require('../config/db'); 

router.get('/dashboard', async (req, res) => {
  try {
    const [totalParrainages] = await db.query('SELECT COUNT(*) AS total FROM parrainages');
    const [totalCandidats] = await db.query('SELECT COUNT(*) AS total FROM candidats');
    const [totalElecteurs] = await db.query('SELECT COUNT(*) AS total FROM electeurs');

    res.json({
      totalParrainages: totalParrainages[0].total,
      totalCandidats: totalCandidats[0].total,
      totalElecteurs: totalElecteurs[0].total
    });
  } catch (error) {
    res.status(500).json({ message: 'Erreur serveur', error });
  }
});

module.exports = router;
