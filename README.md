# SAE 2.01 & 2.04 : Surveillance de la Qualité de l'Eau

## Présentation du Projet
Ce projet, réalisé dans le cadre du BUT Informatique, est une application web permettant de suivre la qualité de l'eau sur le territoire français.

Il répond à une problématique d'architecture de données hybride : comment optimiser les performances en mélangeant des données locales et des données distantes ?

**Objectif :** Fournir une interface de visualisation des stations de mesure et de leurs analyses physico-chimiques en temps réel via l'API nationale **Hub'eau**.

## Architecture Technique (Hybride)
L'application respecte strictement le patron de conception **MVC (Modèle-Vue-Contrôleur)** et sépare les données en deux catégories pour optimiser la charge réseau :

1.  **Données Statiques (Stockage Local - PostgreSQL)** :
    * Les informations invariables (emplacement des stations, coordonnées GPS) sont stockées dans une base de données locale pour un affichage rapide sur la carte.
2.  **Données Dynamiques (API Hub'eau)** :
    * Les relevés de qualité (température, pH, nitrates) sont récupérés en temps réel via l'API externe uniquement lorsque l'utilisateur sélectionne une station.

## Stack Technologique
* **Langage :** Python 3
* **Web Framework :** Flask (Gestion des routes et du templating Jinja2)
* **Base de Données :** PostgreSQL (Script de création et d'importation des données statiques)
* **API Externe :** Hub'eau (Qualité des cours d'eau)
* **Front-End :** HTML5, CSS3, JavaScript (Affichage dynamique)

## Structure du Code
* `controller.py` : Le contrôleur principal qui gère les requêtes HTTP et l'orchestration.
* `/model` : Contient la logique métier et les interactions avec la BDD PostgreSQL (`acces_postgre.py`).
* `/templates` : Les vues HTML de l'application.
* `/static` : Fichiers CSS et images (Architecture MVC).
* `script_admin` : Scripts d'automatisation pour peupler la base de données locale à partir des référentiels nationaux.

---
*Projet validant les compétences de développement d'application (SAE 2.01) et d'exploitation de base de données (SAE 2.04).*
