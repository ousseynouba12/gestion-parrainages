const express = require("express");
const router = express.Router();
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const db = require("../config/db");


const upload = multer({ dest: "uploads/" });


const verifieElecteur = (electeur) => {
    const errors = [];

    if (!/^\d{12}$/.test(electeur.numero_carte)) {
        errors.push("Numéro de carte invalide");
    }
    if (!/^\d+$/.test(electeur.numero_electeur)) {
        errors.push("Numéro d'électeur invalide");
    }
    if (!electeur.nom || !electeur.date_naissance || !electeur.lieu_naissance || !electeur.sexe) {
        errors.push("Informations manquantes");
    }
    if (electeur.sexe !== "M" && electeur.sexe !== "F") {
        errors.push("Sexe invalide");
    }

    return errors.length > 0 ? errors.join(", ") : null;
};


router.post("/upload", upload.single("file"), async (req, res) => {
    const filePath = req.file.path;
    let electeurs = [];

    fs.createReadStream(filePath)
        .pipe(csv({ separator: ";" })) 
        .on("data", (row) => {
            const erreur = verifieElecteur(row);
            electeurs.push({ ...row, erreur });
        })
        .on("end", async () => {
            fs.unlinkSync(filePath);
            const insertQuery = `INSERT INTO electeurs_temp (numero_carte, numero_electeur, nom, prenom, date_naissance, lieu_naissance, sexe, erreur)
                                VALUES ?`;

            const values = electeurs.map(e => [e.numero_carte, e.numero_electeur, e.nom, e.prenom, e.date_naissance, e.lieu_naissance, e.sexe, e.erreur]);

            db.query(insertQuery, [values], (err) => {
                if (err) {
                    console.error("Erreur lors de l'import :", err);
                    return res.status(500).json({ message: "Erreur lors de l'importation." });
                }
                res.status(200).json({ message: "Importation terminée.", electeurs });
            });
        });
});

module.exports = router;
