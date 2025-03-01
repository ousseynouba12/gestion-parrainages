const express = require('express');
const router = express.Router();
const db = require('../config/db');

// Définir la période de parrainage
router.post('/set', async (req, res) => {
    const { startDate, endDate } = req.body;

    if (new Date(startDate) >= new Date(endDate)) {
        return res.status(400).json({ message: "La date de début doit être inférieure à la date de fin." });
    }

    db.query("DELETE FROM periode", (err) => {
        if (err) return res.status(500).json({ message: "Erreur de suppression de la période existante." });

        const sql = "INSERT INTO periode (startDate, endDate) VALUES (?, ?)";
        db.query(sql, [startDate, endDate], (err, result) => {
            if (err) return res.status(500).json({ message: "Erreur lors de l'enregistrement." });

            res.status(200).json({ message: "Période de parrainage enregistrée !" });
        });
    });
});

// Récupérer la période actuelle
router.get('/', (req, res) => {
    db.query("SELECT * FROM periode LIMIT 1", (err, result) => {
        if (err) return res.status(500).json({ message: "Erreur lors de la récupération." });

        if (result.length === 0) {
            return res.status(404).json({ message: "Aucune période enregistrée." });
        }
        res.status(200).json(result[0]);
    });
});

module.exports = router;
