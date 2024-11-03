from requests import get
from typing import Any, List, Dict, Tuple
from logging import error, debug


def query_api(url: str) -> Any:
    debug(f"Sending Query: {url}")
    response = get(url)
    if response.status_code != 200:
        error(f"Failed to query: {url}") 
        raise Exception(f"Failed to query: {url}")
    
    debug(f"Response: {response.json()}")
    return response.json()


def users_info(handles: List[str]) -> List[Dict[str, Any]]:
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    return query_api(url)["result"]


def user_rating(handle: str) -> List[Any]:
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    return query_api(url)["result"]


def user_status(handle: str, count: int = 100) -> List[Any]:
    url = f"https://codeforces.com/api/user.status?handle={handle}&count={count}"
    return query_api(url)["result"]

def problemset_problems() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    url = "https://codeforces.com/api/problemset.problems"
    data = query_api(url)
    return data["result"]["problems"], data["result"]["problemStatistics"]