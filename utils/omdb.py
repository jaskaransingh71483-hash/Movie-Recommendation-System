# utils/omdb.py
import requests

def fetch_omdb_metadata(title, api_key):
    """Retrieve poster and detailed plot description from OMDb API."""
    if not api_key or api_key == "your_omdb_api_key":
        return "N/A", "N/A"
        
    url = "http://www.omdbapi.com/"
    try:
        # Pass params as dict to automatically handle URL encoding
        res = requests.get(url, params={"t": title, "plot": "full", "apikey": api_key}, timeout=5).json()
        if res.get("Response") == "True":
            plot = res.get("Plot", "N/A")
            poster = res.get("Poster", "N/A")
            return plot, poster
    except Exception:
        # Fail gracefully on network timeout or connection error
        pass
        
    return "N/A", "N/A"
