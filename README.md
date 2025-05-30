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
pip install -r requirements.txt
```

## Configuration

Avant d'exécuter le script, vous devez configurer les variables d'environnement suivantes pour l'authentification à l'API de l'OMS :

- `ICD_API_TOKEN_ENDPOINT` : L'URL du point de terminaison pour obtenir le jeton d'accès.
- `ICD_API_CLIENT_ID` : Votre identifiant client pour l'API.
- `ICD_API_CLIENT_SECRET` : Votre secret client pour l'API.

Vous pouvez définir ces variables d'environnement de la manière suivante :

**Linux/macOS :**

```bash
export ICD_API_TOKEN_ENDPOINT="your_token_endpoint"
export ICD_API_CLIENT_ID="your_client_id"
export ICD_API_CLIENT_SECRET="your_client_secret"
```

**Windows (Invite de commandes) :**

```bash
set ICD_API_TOKEN_ENDPOINT="your_token_endpoint"
set ICD_API_CLIENT_ID="your_client_id"
set ICD_API_CLIENT_SECRET="your_client_secret"
```

**Windows (PowerShell) :**

```powershell
$env:ICD_API_TOKEN_ENDPOINT="your_token_endpoint"
$env:ICD_API_CLIENT_ID="your_client_id"
$env:ICD_API_CLIENT_SECRET="your_client_secret"
```

Remplacez `"your_token_endpoint"`, `"your_client_id"`, et `"your_client_secret"` par vos informations d'identification réelles.

### Configuration des URLs de Chapitre (chapter_urls.txt)

Le script peut lire une liste d'URLs de chapitres ICD-11 à partir d'un fichier nommé `chapter_urls.txt` situé à la racine du projet.

- Chaque ligne du fichier doit correspondre à une URL de chapitre complète.
- Les lignes vides sont ignorées.
- Les lignes commençant par un `#` sont considérées comme des commentaires et sont ignorées.

**Exemple de contenu pour `chapter_urls.txt`:**
```
http://id.who.int/icd/entity/426429380
# Ceci est un commentaire, cette ligne est ignorée
http://id.who.int/icd/entity/another-chapter-id
```

Si le fichier `chapter_urls.txt` n'est pas trouvé, ou s'il est vide après avoir ignoré les commentaires et les lignes vides, le script utilisera une liste d'URLs de chapitre par défaut codée en dur (contenant généralement une ou deux URLs d'exemple pour la démonstration). Un message de log indiquera si le fichier est utilisé ou si le script se rabat sur la liste par défaut.

### Note on SSL Verification

Par défaut, la vérification SSL est activée pour toutes les requêtes afin de garantir la sécurité des communications. Cependant, les utilisateurs se trouvant derrière certains proxys d'entreprise ou ayant des configurations réseau spécifiques pourraient rencontrer des erreurs liées à SSL (par exemple, `SSLCertVerificationError`).

Si vous rencontrez de tels problèmes et que vous comprenez les implications en matière de sécurité, vous devrez peut-être examiner la configuration de votre proxy ou les certificats SSL de votre système. En dernier recours, vous pouvez consulter la documentation de `aiohttp` pour obtenir des conseils sur la gestion des contextes SSL et la configuration des certificats approuvés. Il est fortement déconseillé de désactiver la vérification SSL de manière globale sans comprendre les risques.

## Utilisation

### 1. Clonez le dépôt

Clonez le projet sur votre machine locale :

```bash
git clone https://github.com/Abusooma/scraping-de-maladies-API-ICD.git
cd ai_voice
```

### 2. Exécutez le script

Dans le répertoire principal du projet, exécutez le script Python pour récupérer les données des maladies :

```bash
python api.py
```

Le script va interroger l'API de l'OMS, récupérer les données et les sauvegarder dans un fichier JSON nommé `icd11_data.json`.

### 3. Structure du fichier JSON

Le fichier `icd11_data.json` généré contient une structure hiérarchique. L'objet racine a une clé `"ICD-11"` qui contient `"releaseId"` et une liste de `"chapitres"`. Chaque chapitre, et chaque entité imbriquée, aura la structure suivante :

- **`nom`**: Le nom de l'entité (par exemple, maladie, chapitre). Valeur extraite du champ `title` de l'API.
- **`id`**: L'identifiant unique de l'entité, dérivé de l'URL de l'API.
- **`description`**: La définition ou description de l'entité. Provient du champ `definition` de l'API, ou affiche `"Definition not found"` / `"Définition non trouvée"` si l'information n'est pas disponible ou si la langue demandée n'a pas de définition.
- **`categories`** ou **`subcategories`**: Une liste d'entités enfants qui représentent la hiérarchie.
    - Les entités de premier niveau (directement sous un "chapitre") auront leurs enfants listés sous la clé `"categories"`.
    - Les entités imbriquées (enfants d'autres entités) auront leurs enfants listés sous la clé `"subcategories"`.
    - Si une entité n'a pas d'enfants, cette clé ne sera pas présente.

Notez que les champs tels que `code` ou `symptômes` ne sont pas directement extraits par ce script dans sa version actuelle.

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
