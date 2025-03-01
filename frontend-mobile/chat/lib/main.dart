import 'dart:math';
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: CandidateInputScreen(),
    );
  }
}

class CandidateInputScreen extends StatefulWidget {
  @override
  _CandidateInputScreenState createState() => _CandidateInputScreenState();
}

class _CandidateInputScreenState extends State<CandidateInputScreen> {
  final _voterCardController = TextEditingController();
  final _cinController = TextEditingController();
  final _verificationCodeController = TextEditingController();
  String _verificationCode = '';
  bool _isCodeSent = false;
  bool _isCINValid = true;
  bool _isLoading = false;
  bool _isVoterCardValid = true;
  bool _isCandidateRegistered = false;
  bool _isCodeValid = false;

  // Simuler une base de données de cartes électorales
  final List<String> _registeredVoterCards = [
    '1234567890', '2345678901', '3456789012' // Exemple de numéros valides
  ];

  // Simuler une base de données de candidats
  final Map<String, String> _candidates = {
    '1234567890': 'Hawa',
    '2345678901': 'Fatou',
    '3456789012': 'Ndeye',
  };

  // Fonction pour générer un code de vérification aléatoire
  String _generateVerificationCode() {
    final random = Random();
    return (random.nextInt(900000) + 100000).toString(); // Génère un code de 6 chiffres
  }

  // Fonction pour vérifier le CIN (ici, le format est un exemple)
  bool _isCinValid(String cin) {
    // Exemple : le CIN commence par une lettre suivie de 7 chiffres
    RegExp cinRegExp = RegExp(r'^[A-Za-z]\d{7}$');
    return cinRegExp.hasMatch(cin);
  }

  // Fonction pour simuler l'envoi du code de vérification et l'afficher dans le terminal
  Future<void> _sendVerificationCode() async {
    setState(() {
      _isLoading = true;
    });

    if (_isCinValid(_cinController.text)) {
      // Simuler l'envoi du code (on l'affiche dans le terminal)
      await Future.delayed(Duration(seconds: 2), () {
        setState(() {
          _verificationCode = _generateVerificationCode();
          _isCodeSent = true;
          _isCINValid = true;
          _isLoading = false;
        });
      });

      // Afficher le code de vérification dans le terminal
      print('Le code de vérification est : $_verificationCode');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Code de vérification généré !')),
      );
    } else {
      setState(() {
        _isLoading = false;
        _isCINValid = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('CIN invalide, veuillez réessayer.')),
      );
    }
  }

  // Fonction pour valider le code
  void _validateCode() {
    if (_verificationCodeController.text == _verificationCode) {
      setState(() {
        _isCodeValid = true; // Code valide
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Code de vérification validé !')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Code incorrect, veuillez réessayer.')),
      );
    }
  }

  // Fonction pour valider le numéro de la carte d'électeur
  void _validateVoterCard() {
    if (_voterCardController.text.isEmpty) {
      setState(() {
        _isVoterCardValid = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Veuillez entrer un numéro de carte d\'électeur.')),
      );
      return;
    }

    if (_registeredVoterCards.contains(_voterCardController.text)) {
      setState(() {
        _isCandidateRegistered = true; // Candidat déjà enregistré
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Candidat déjà enregistré !')),
      );
    } else {
      setState(() {
        _isVoterCardValid = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Le candidat considéré n\'est pas présent dans le fichier électoral.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0A0E21), // Fond bleu de nuit
      appBar: AppBar(
        title: Text('Saisie Candidat'),
        backgroundColor: Color(0xFF1D1E33), // AppBar bleu de nuit plus foncé
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Ajoutez un nouveau candidat',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.blueAccent, // Texte bleu ciel
              ),
            ),
            SizedBox(height: 30),

            // Champ de saisie du numéro de la carte d'électeur
            TextField(
              controller: _voterCardController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Numéro de la carte d\'électeur',
                hintText: 'Exemple: 1234567890',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.credit_card, color: Colors.blueAccent), // Icône bleu ciel
                errorText: !_isVoterCardValid ? 'Numéro incorrect ou non trouvé' : null,
              ),
            ),
            SizedBox(height: 20),

            // Bouton pour valider la carte d'électeur
            ElevatedButton(
              onPressed: _validateVoterCard,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color.fromARGB(255, 12, 33, 68), // Bouton bleu ciel
                padding: EdgeInsets.symmetric(vertical: 15),
              ),
              child: Text(
                'Vérifier la carte d\'électeur',
                style: TextStyle(fontSize: 16, color: Colors.white),
              ),
            ),
            SizedBox(height: 20),

            // Si le candidat est validé, afficher le champ CIN
            if (_isCandidateRegistered)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: _cinController,
                    keyboardType: TextInputType.text,
                    decoration: InputDecoration(
                      labelText: 'Numéro CIN',
                      hintText: 'Exemple: A1234567',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.credit_card, color: Colors.blueAccent), // Icône bleu ciel
                      errorText: !_isCINValid ? 'Format CIN invalide' : null,
                    ),
                  ),
                  SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _sendVerificationCode,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent, // Bouton bleu ciel
                      padding: EdgeInsets.symmetric(vertical: 15),
                    ),
                    child: _isLoading
                        ? CircularProgressIndicator(color: Colors.white)
                        : Text(
                            'Envoyer le code de vérification',
                            style: TextStyle(fontSize: 16, color: Colors.white),
                          ),
                  )
                ],
              ),

            // Si le code est envoyé, afficher le champ pour entrer le code
            if (_isCodeSent)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 20),
                  TextField(
                    controller: _verificationCodeController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'Entrez le code de vérification',
                      hintText: 'Exemple: 123456',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.lock, color: Colors.blueAccent), // Icône bleu ciel
                    ),
                  ),
                  SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _validateCode,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent, // Bouton bleu ciel
                      padding: EdgeInsets.symmetric(vertical: 15),
                    ),
                    child: Text(
                      'Valider le code',
                      style: TextStyle(fontSize: 16, color: Colors.white),
                    ),
                  ),
                ],
              ),

            // Si la carte d'électeur est incorrecte, afficher un message d'erreur
            if (!_isVoterCardValid && !_isCandidateRegistered)
              Text(
                'Le candidat considéré n\'est pas présent dans le fichier électoral.',
                style: TextStyle(fontSize: 14, color: Colors.red),
              ),

            // Si le code est valide, afficher les informations du candidat
            if (_isCodeValid)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Informations du Candidat:',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    SizedBox(height: 10),
                    Text('Nom: ${_candidates[_voterCardController.text]}', style: TextStyle(color: Colors.white)),
                    Text('CIN: ${_cinController.text}', style: TextStyle(color: Colors.white)),
                    Text('Carte électeur: ${_voterCardController.text}', style: TextStyle(color: Colors.white)),
                  ],
                ),
              ),
            SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}