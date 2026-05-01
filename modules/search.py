import requests

def search_medicine_info(medicine_name: str) -> str:
    """
    Return a placeholder so the LLM uses its own knowledge.
    DuckDuckGo blocks requests from cloud servers, so we skip scraping.
    """
    return f"Please use your medical knowledge to provide information about {medicine_name}."
