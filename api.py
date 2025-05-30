import asyncio
import aiohttp
import json
import os
import logging
from typing import List, Dict, Any, NamedTuple, Optional
from aiohttp import ClientSession, TCPConnector
from urllib.parse import urlparse, urlunparse

# Define NamedTuple for entity data
class EntityData(NamedTuple):
    info: Optional[Dict[str, Any]]
    child_urls: List[str]

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File containing chapter URLs
CHAPTER_URLS_FILE = 'chapter_urls.txt'

# Configuration API
TOKEN_ENDPOINT = os.environ.get('ICD_API_TOKEN_ENDPOINT')
CLIENT_ID = os.environ.get('ICD_API_CLIENT_ID')
CLIENT_SECRET = os.environ.get('ICD_API_CLIENT_SECRET')
SCOPE = 'icdapi_access'
GRANT_TYPE = 'client_credentials'

# Check if environment variables are set
if not TOKEN_ENDPOINT:
    logger.error("The environment variable ICD_API_TOKEN_ENDPOINT is not set.")
    exit(1)
if not CLIENT_ID:
    logger.error("The environment variable ICD_API_CLIENT_ID is not set.")
    exit(1)
if not CLIENT_SECRET:
    logger.error("The environment variable ICD_API_CLIENT_SECRET is not set.")
    exit(1)


async def get_access_token(session: ClientSession) -> str:
    """Get access token from ICD-11 API"""
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': SCOPE,
        'grant_type': GRANT_TYPE
    }

    try:
        async with session.post(TOKEN_ENDPOINT, data=payload) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data['access_token']
    except Exception as e:
        logger.error(f"Error getting token: {e}")
        raise


def format_url(url: str) -> str:
    """Format URL to HTTPS using urllib.parse"""
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'http':
        # Create a new parsed URL with the https scheme
        parsed_url = parsed_url._replace(scheme='https')
    return urlunparse(parsed_url)


async def fetch_url(
    session: ClientSession,
    url: str,
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """Fetch data from a URL with concurrency management"""
    async with semaphore:
        uri = format_url(url)
        # aiohttp specific exceptions (ClientResponseError, ClientConnectionError)
        # will propagate and be handled in extract_entity_info.
        async with session.get(uri, headers=headers) as response:
            response.raise_for_status()  # Raises an exception for HTTP error codes (4xx or 5xx)
            return await response.json()


async def extract_entity_info(
    session: ClientSession,
    url: str,
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore
) -> EntityData:
    """Extract entity information"""
    try:
        result = await fetch_url(session, url, headers, semaphore)
    except aiohttp.ClientError as e:
        logger.error(f"Client error while fetching {url}: {e}")
        return EntityData(info=None, child_urls=[])
    except Exception as e: # Capture other potential exceptions from fetch_url
        logger.error(f"Unexpected error while fetching {url}: {e}")
        return EntityData(info=None, child_urls=[])

    if not result: # In case fetch_url returns None or an empty dict for a non-exceptional reason
        logger.warning(f"No data received from {url} without explicit exception.")
        return EntityData(info=None, child_urls=[])

    entity_info = {
        "nom": result.get('title', {}).get('@value', 'Name not found'),
        "id": url.split("/")[-1],
        "description": result.get("definition", {}).get('@value', "Definition not found")
    }

    return EntityData(info=entity_info, child_urls=result.get('child', []))


async def crawl_hierarchy(
    session: ClientSession,
    urls: List[str],
    headers: Dict[str, str],
    semaphore: asyncio.Semaphore,
    depth: int = 0
) -> List[Dict[str, Any]]:
    """Asynchronously crawl the ICD-11 hierarchy"""
    tasks = [
        extract_entity_info(session, url, headers, semaphore)
        for url in urls
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    entities = []
    for result in results:
        # Handle potential exceptions
        if isinstance(result, Exception):
            logger.error(f"Error during processing: {result}")
            continue

        # result is now an EntityData instance or an exception
        entity_data: EntityData = result

        # If extract_entity_info returned EntityData(info=None, ...), we handle it here
        if entity_data.info is None:
            # The specific error has already been logged in extract_entity_info
            continue

        # Recursive processing of subcategories
        if entity_data.info and entity_data.child_urls: # Ensure entity_info is not None
            depth_key = 'categories' if depth == 0 else 'subcategories'
            entity_data.info[depth_key] = await crawl_hierarchy(
                session,
                entity_data.child_urls,
                headers,
                semaphore,
                depth + 1
            )

        entities.append(entity_data.info)

    return entities


async def main():
    # Default chapter URLs if the file is not found or empty
    default_chapter_urls = [
        'http://id.who.int/icd/entity/426429380',
        # ... (add all your chapter URLs here for fallback)
    ]
    chapter_urls = []

    if os.path.exists(CHAPTER_URLS_FILE):
        try:
            with open(CHAPTER_URLS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        chapter_urls.append(line)
            if chapter_urls:
                logger.info(f"Successfully read {len(chapter_urls)} URLs from {CHAPTER_URLS_FILE}.")
            else:
                logger.warning(f"{CHAPTER_URLS_FILE} is empty. Using default chapter URLs.")
                chapter_urls = default_chapter_urls
        except IOError as e:
            logger.error(f"Error reading {CHAPTER_URLS_FILE}: {e}. Using default chapter URLs.")
            chapter_urls = default_chapter_urls
    else:
        logger.warning(f"{CHAPTER_URLS_FILE} not found. Using default chapter URLs.")
        chapter_urls = default_chapter_urls

    if not chapter_urls:
        logger.error("No chapter URLs to process. Exiting. Please create chapter_urls.txt or define default_chapter_urls.")
        return

    # Secure connection and limitation of simultaneous connections
    connector = TCPConnector(limit=10)

    async with aiohttp.ClientSession(connector=connector) as session:
        # Get token
        token = await get_access_token(session)

        # Configure headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Accept-Language': 'en', # Changed from 'fr' to 'en'
            'API-Version': 'v2'
        }

        # Semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(10)

        # Crawl hierarchy
        debut = asyncio.get_event_loop().time()
        chapitres = await crawl_hierarchy(session, chapter_urls, headers, semaphore)
        fin = asyncio.get_event_loop().time()

        # Final data structure
        data = {
            "ICD-11": {
                "releaseId": "2025-01",
                "chapitres": chapitres # "chapitres" key kept as is, assuming it's a data key
            }
        }

        # Saving JSON
        with open('icd11_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Execution time: {fin - debut:.2f} seconds")
        return data

if __name__ == "__main__":
    asyncio.run(main())
