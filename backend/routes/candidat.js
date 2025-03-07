const express = require('express');
const router = express.Router();
const db = require('../config/db'); 


router.post('/candidats', (req, res) => {
  const { nom, prenom, dateNaissance, partiPolitique } = req.body;
  
  const query = 'INSERT INTO candidats (nom, prenom, date_naissance, parti_politique) VALUES (?, ?, ?, ?)';
  db.query(query, [nom, prenom, dateNaissance, partiPolitique], (err, result) => {
    if (err) {
      return res.status(500).json({ message: 'Erreur lors de l\'ajout du candidat', error: err });
    }
    res.status(201).json({ message: 'Candidat ajouté avec succès', id: result.insertId });
  });
});

module.exports = router;
