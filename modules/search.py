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
    """Search for medicine info using multiple specific queries."""

    # Multiple targeted queries — brand name specific
    queries = [
        f"{medicine_name} eye drops uses side effects",
        f"{medicine_name} drug information",
        f"{medicine_name} medicine what is it used for",
    ]

    all_urls = []
    for query in queries:
        urls = _duckduckgo_search(query)
        for url in urls:
            if url not in all_urls:
                all_urls.append(url)

    if not all_urls:
        return ""

    # Filter: keep only URLs that contain the medicine name in the URL
    medicine_slug = medicine_name.lower().replace(" ", "")
    relevant_urls = [
        u for u in all_urls
        if any(word.lower() in u.lower()
               for word in medicine_name.split())
    ]

    # If no relevant URLs found, fall back to all URLs
    if not relevant_urls:
        relevant_urls = all_urls

    # Prioritize trusted domains
    trusted_urls = _prioritize_trusted(relevant_urls)

    collected_text = []
    for url in trusted_urls[:MAX_RESULTS]:
        content = _extract_page_content(url, medicine_name)
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


def _extract_page_content(url: str, medicine_name: str = "") -> str:
    """Visit a URL and extract only relevant content about the medicine."""
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

        # Remove clutter
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

        # Filter: keep only paragraphs that mention the medicine name
        if medicine_name:
            medicine_words = medicine_name.lower().split()
            relevant_lines = []
            for line in lines:
                line_lower = line.lower()
                # Keep lines mentioning the medicine or general medical terms
                if (any(word in line_lower for word in medicine_words) or
                    any(term in line_lower for term in [
                        "side effect", "warning", "dosage", "storage",
                        "used for", "treat", "consult", "doctor", "symptom",
                        "indication", "precaution", "interaction"
                    ])):
                    relevant_lines.append(line)

            # Use relevant lines if found, else fall back to all lines
            lines = relevant_lines if len(relevant_lines) > 10 else lines

        return "\n".join(lines)[:MAX_CONTENT_CHARS]

    except Exception as e:
        print(f"[Scrape Error] {url}: {e}")
        return ""
