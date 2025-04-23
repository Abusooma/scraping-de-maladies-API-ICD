# Scraping de Maladies (API - ICD)

Ce Script permet de récupérer des informations sur toutes les maladies de la **Classification Internationale des Maladies** (ICD) en utilisant l'API de l'OMS (Organisation Mondiale de la Santé). Le script récupère les données des maladies et les génère sous forme de fichier **JSON**. Ce projet est idéal pour les chercheurs ou développeurs intéressés par l'accès à des données médicales structurées.

## Fonctionnalités

- Récupère les informations de toutes les maladies à partir de l'API **ICD** de l'OMS.
- Exporte les données récupérées dans un fichier **JSON**.
- Organise les informations de manière structurée et facilement exploitable.
  
## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils et dépendances suivants :

- **Python** (version 3.6 ou supérieure)
- **pip** pour l'installation des packages Python

### Dépendances

Installez les bibliothèques nécessaires en utilisant `pip` :

```bash
pip install requests
```

## Utilisation

### 1. Clonez le dépôt

Clonez le projet sur votre machine locale :

```bash
git clone https://github.com/votre_utilisateur/icd-scraping.git
cd icd-scraping
```

### 2. Exécutez le script

Dans le répertoire principal du projet, exécutez le script Python pour récupérer les données des maladies :

```bash
python scraper.py
```

Le script va interroger l'API de l'OMS, récupérer les données et les sauvegarder dans un fichier JSON nommé `icd_data.json`.

### 3. Structure du fichier JSON

Le fichier généré `icd_data.json` contiendra une liste d'objets JSON avec les informations suivantes pour chaque maladie :

- **code** : Le code de la maladie selon la classification ICD.
- **nom** : Le nom de la maladie.
- **description** : Une description détaillée de la maladie.
- **symptômes** : Une liste des symptômes associés à la maladie.
- **catégorie** : La catégorie à laquelle la maladie appartient dans l'ICD.

### 4. Exemple de sortie (JSON)

Voici un extrait d'exemple du fichier JSON généré :

```json
 {
                    "nom": "Chondrosarcome, localisation primitive",
                    "id": "1625755389",
                    "description": "Définition non trouvée",
                    "subcategories": [
                      {
                        "nom": "Chondrosarcome myxoïde extrasquelettique d'autres localisations précisées",
                        "id": "782606527",
                        "description": "Définition non trouvée"
                      },
                      {
                        "nom": "Chondrosarcome extrasquelettique myxoïde des tissus mous du membre",
                        "id": "617665544",
                        "description": "Définition non trouvée"
                      },
                      {
                        "nom": "Chondrosarcome extrasquelettique myxoïde, localisation inconnue",
                        "id": "834676499",
                        "description": "Définition non trouvée"
                      },
                      {
                        "nom": "Chondrosarcome osseux ou du cartilage articulaire des membres",
                        "id": "2072379825",
                        "description": "Définition non trouvée"
                      },
                      {
                        "nom": "Chondrosarcome osseux ou du cartilage articulaire du pelvis",
                        "id": "1493554134",
                        "description": "Définition non trouvée",
                        "subcategories": [
                          {
                            "nom": "Chondrosarcome osseux ou du cartilage articulaire des os pelviens, du sacrum ou du coccyx",
                            "id": "387820742",
                            "description": "Définition non trouvée"
                          }
                        ]
                      },
                      {
                        "nom": "Chondrosarcome osseux ou du cartilage articulaire des côtes, du sternum ou de la clavicule",
                        "id": "1985099973",
                        "description": "Définition non trouvée"
                      },
                      {
                        "nom": "Chondrosarcome osseux ou du cartilage articulaire d'autres localisations précisées",
                        "id": "1510754862",
                        "description": "Définition non trouvée",
                        "subcategories": [
                          {
                            "nom": "Chondrosarcome osseux ou du cartilage articulaire de la mandibule",
                            "id": "993091882",
                            "description": "Définition non trouvée"
                          },
                          {
                            "nom": "Chondrosarcome de l'os ou du cartilage articulaire du crâne ou du visage",
                            "id": "431141709",
                            "description": "Définition non trouvée",
                            "subcategories": [
                              {
                                "nom": "Tumeur maligne du cartilage du nez",
                                "id": "714224127",
                                "description": "Définition non trouvée"
                              }
                            ]
                          },
                          {
                            "nom": "Chondrosarcome de l'os ou du cartilage articulaire de la côlonne vertébrale",
                            "id": "34430941",
                            "description": "Définition non trouvée"
                          }
                        ]
                      }
                    ]
}
```
