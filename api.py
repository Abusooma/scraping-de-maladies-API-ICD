import asyncio
import aiohttp
import json
import os
import logging
from typing import List, Dict, Any
from aiohttp import ClientSession, TCPConnector
from urllib.parse import urlparse

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration API
TOKEN_ENDPOINT = 'https://icdaccessmanagement.who.int/connect/token'
CLIENT_ID = 'ec996916-7bd2-4fab-b15c-5aee87a67702_0e02736c-d704-4860-a7a2-8885dbae0ed8'
CLIENT_SECRET = '13YrLGs/VEVW7IqQ/W4zU/How7w/jmpAgGQBBgYjkyY='
SCOPE = 'icdapi_access'
GRANT_TYPE = 'client_credentials'


async def get_access_token(session: ClientSession) -> str:
    """Obtenir le jeton d'accès de l'API ICD-11"""
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': SCOPE,
        'grant_type': GRANT_TYPE
    }

    try:
        async with session.post(TOKEN_ENDPOINT, data=payload, ssl=False) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data['access_token']
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention du token : {e}")
        raise


def format_url(url: str) -> str:
    """Formater l'URL en HTTPS"""
    return url.replace('http:', 'https:')


async def fetch_url(
    session: ClientSession,
    url: str,
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """Récupérer les données d'une URL avec gestion de la concurrence"""
    async with semaphore:
        uri = format_url(url)
        try:
            async with session.get(uri, headers=headers, ssl=False) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Erreur de requête pour {url}: {e}")
            return {}


async def extract_entity_info(
    session: ClientSession,
    url: str,
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """Extraire les informations d'une entité"""
    result = await fetch_url(session, url, headers, semaphore)

    if not result:
        return {}

    entity_info = {
        "nom": result.get('title', {}).get('@value', 'Nom non trouvé'),
        "id": url.split("/")[-1],
        "description": result.get("definition", {}).get('@value', "Définition non trouvée")
    }

    return entity_info, result.get('child', [])


async def crawl_hierarchy(
    session: ClientSession,
    urls: List[str],
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore,
    depth: int = 0
) -> List[Dict[str, Any]]:
    """Crawler de manière asynchrone la hiérarchie ICD-11"""
    tasks = [
        extract_entity_info(session, url, headers, semaphore)
        for url in urls
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    entities = []
    for result in results:
        # Gérer les potentielles exceptions
        if isinstance(result, Exception):
            logger.error(f"Erreur lors du traitement: {result}")
            continue

        if not result:
            continue

        entity_info, child_urls = result

        # Traitement récursif des sous-catégories
        if child_urls:
            depth_key = 'categories' if depth == 0 else 'subcategories'
            entity_info[depth_key] = await crawl_hierarchy(
                session,
                child_urls,
                headers,
                semaphore,
                depth + 1
            )

        entities.append(entity_info)

    return entities


async def main():
    # URLs des chapitres
    chapter_urls = [
        'http://id.who.int/icd/entity/426429380',
        # ... (ajoutez toutes vos URLs de chapitre)
    ]

    # Connexion sécurisée et limitation du nombre de connexions simultanées
    connector = TCPConnector(limit=10, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        # Obtenir le token
        token = await get_access_token(session)

        # Configurer les en-têtes
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Accept-Language': 'fr',
            'API-Version': 'v2'
        }

        # Semaphore pour limiter le nombre de requêtes concurrentes
        semaphore = asyncio.Semaphore(10)

        # Crawl de la hiérarchie
        debut = asyncio.get_event_loop().time()
        chapitres = await crawl_hierarchy(session, chapter_urls, headers, semaphore)
        fin = asyncio.get_event_loop().time()

        # Structure de données finale
        data = {
            "ICD-11": {
                "releaseId": "2025-01",
                "chapitres": chapitres
            }
        }

        # Enregistrement du JSON
        with open('icd11_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Temps d'exécution : {fin - debut:.2f} secondes")
        return data

if __name__ == "__main__":
    asyncio.run(main())
