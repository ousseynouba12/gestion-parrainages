require('dotenv').config();
const express = require('express');
const cors = require('cors');


const app = express();
app.use(cors());
app.use(express.json());


// Importer les routes
// Ouvrir Fermer Periode Parrainage
const periodeRoutes = require('./routes/periodeRoutes');
app.use('/api/periode', periodeRoutes);

//Importation liste
const uploadRoutes = require("./routes/uploadRoutes");
app.use("/api/upload", uploadRoutes);

//Statistique
const dashboardRoutes = require('./routes/dashboard');
app.use('/api/stat', dashboardRoutes);



const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Serveur lancé sur le port ${PORT}`));
