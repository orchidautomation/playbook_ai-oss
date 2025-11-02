"""
Firecrawl Helper Functions
Wrapper functions for Firecrawl Python SDK operations.
"""

from firecrawl import Firecrawl
from typing import Dict, List
import config

# Initialize Firecrawl client
fc = Firecrawl(api_key=config.FIRECRAWL_API_KEY)


def map_website(domain: str, limit: int = None) -> Dict:
    """
    Map website to discover all URLs.

    Args:
        domain: Domain to map (e.g., "https://example.com")
        limit: Maximum number of URLs to discover (default: from config)

    Returns:
        Dict with keys: success, domain, urls, total_urls, error (if failed)
    """
    if limit is None:
        limit = config.MAX_URLS_TO_MAP

    try:
        result = fc.map(url=domain, limit=limit)
        # Firecrawl returns a MapData object with .links attribute containing LinkResult objects
        link_results = result.links if hasattr(result, 'links') else []

        # Extract just the URL strings from LinkResult objects
        urls = [link.url if hasattr(link, 'url') else str(link) for link in link_results]

        return {
            "success": True,
            "domain": domain,
            "urls": urls,
            "total_urls": len(urls)
        }
    except Exception as e:
        return {
            "success": False,
            "domain": domain,
            "error": str(e),
            "urls": [],
            "total_urls": 0
        }


def scrape_url(url: str, formats: List[str] = None) -> Dict:
    """
    Scrape a single URL.

    Args:
        url: URL to scrape
        formats: List of formats to return (default: from config)

    Returns:
        Dict with keys: success, url, markdown, html, metadata, error (if failed)
    """
    if formats is None:
        formats = config.DEFAULT_SCRAPE_FORMATS

    try:
        result = fc.scrape(
            url,
            formats=formats,
            wait_for=config.SCRAPE_WAIT_TIME,
            max_age=config.SCRAPE_MAX_AGE  # 500% faster with cached data!
        )

        # Firecrawl returns a ScrapeData object with attributes
        metadata = getattr(result, 'metadata', {})
        # Convert metadata object to dict if needed
        if hasattr(metadata, '__dict__'):
            metadata = metadata.__dict__
        elif metadata and not isinstance(metadata, dict):
            metadata = {}

        return {
            "success": True,
            "url": url,
            "markdown": getattr(result, 'markdown', ""),
            "html": getattr(result, 'html', ""),
            "metadata": metadata
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e),
            "markdown": "",
            "html": "",
            "metadata": {}
        }


def batch_scrape_urls(urls: List[str], formats: List[str] = None) -> Dict[str, Dict]:
    """
    Batch scrape multiple URLs.

    Args:
        urls: List of URLs to scrape
        formats: List of formats to return (default: markdown only)

    Returns:
        Dict with keys: success, results, total_scraped, error (if failed)
        results is a dict mapping URL -> {markdown, metadata}
    """
    if formats is None:
        formats = config.BATCH_SCRAPE_FORMAT

    try:
        # Use batch_scrape waiter method with wait_timeout parameter
        job = fc.batch_scrape(
            urls,
            formats=formats,
            poll_interval=config.BATCH_SCRAPE_POLL_INTERVAL,
            wait_timeout=config.BATCH_SCRAPE_TIMEOUT,  # Note: wait_timeout, not timeout!
            max_age=config.SCRAPE_MAX_AGE  # 500% faster with cached data!
        )

        # Convert to dict keyed by URL
        results = {}
        for doc in job.data:
            # Get URL from metadata
            url = doc.metadata.source_url if hasattr(doc, 'metadata') and doc.metadata else "unknown"

            # Convert metadata to dict if needed
            metadata = {}
            if hasattr(doc, 'metadata') and doc.metadata:
                if hasattr(doc.metadata, '__dict__'):
                    metadata = doc.metadata.__dict__
                elif isinstance(doc.metadata, dict):
                    metadata = doc.metadata

            results[url] = {
                "markdown": doc.markdown if hasattr(doc, 'markdown') else "",
                "metadata": metadata
            }

        return {
            "success": True,
            "results": results,
            "total_scraped": len(results)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": {},
            "total_scraped": 0
        }
