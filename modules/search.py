import requests
from bs4 import BeautifulSoup
import time

TRUSTED_DOMAINS = [
    "who.int", "fda.gov", "nhs.uk", "mayoclinic.org",
    "medlineplus.gov", "webmd.com", "drugs.com",
    "healthline.com", "rxlist.com", "nih.gov",
]

DDGO_URL = "https://html.duckduckgo.com/html/"
MAX_RESULTS = 5
MAX_CONTENT_CHARS = 3000
REQUEST_TIMEOUT = 10


def search_medicine_info(medicine_name: str) -> str:
    """Search for medicine info from trusted sources."""

    # Simple straightforward queries
    queries = [
        f"{medicine_name} medicine",
        f"{medicine_name} uses side effects",
        f"what is {medicine_name}",
    ]

    all_urls = []
    for query in queries:
        urls = _duckduckgo_search(query)
        for url in urls:
            if url not in all_urls:
                all_urls.append(url)
        if len(all_urls) >= 10:
            break

    if not all_urls:
        return ""

    # Prioritize trusted domains
    trusted_urls = _prioritize_trusted(all_urls)

    collected_text = []
    for url in trusted_urls[:MAX_RESULTS]:
        content = _extract_page_content(url)
        if content and len(content) > 200:
            collected_text.append(f"SOURCE: {url}\n{content}")
            time.sleep(0.5)

    return "\n\n---\n\n".join(collected_text)


def _duckduckgo_search(query: str) -> list:
    """Send a query to DuckDuckGo and return result URLs."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.post(
            DDGO_URL,
            data={"q": query, "kl": "us-en"},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for result in soup.select(".result__a"):
            href = result.get("href", "")
            if href.startswith("http"):
                links.append(href)
        return links
    except Exception as e:
        print(f"[Search Error] {e}")
        return []


def _prioritize_trusted(urls: list) -> list:
    """Sort URLs so trusted medical domains come first."""
    trusted = [u for u in urls if any(d in u for d in TRUSTED_DOMAINS)]
    others  = [u for u in urls if not any(d in u for d in TRUSTED_DOMAINS)]
    return trusted + others


def _extract_page_content(url: str) -> str:
    """Visit a URL and extract clean text content."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form", "iframe"]):
            tag.decompose()

        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find(id="content") or
            soup.body
        )
        if not main_content:
            return ""

        text = main_content.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)[:MAX_CONTENT_CHARS]

    except Exception as e:
        print(f"[Scrape Error] {url}: {e}")
        return ""
