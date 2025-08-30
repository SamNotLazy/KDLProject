# data_loader.py
import os
import requests
import geopandas as gpd
from cache import cache
import config

def get_state_names():
    """
    Fetches the complete list of state names (directory names) from the GitHub repository,
    handling API pagination.

    Returns:
        list[str]: A sorted list of all state names, or an empty list if an error occurs.
    """
    api_url = config.GITHUB_API_BASE_URL + 'INDIAN-SHAPEFILES-master/STATES'
    all_state_names = []
    print(f"Fetching state list from GitHub API: {api_url}")

    while api_url:
        try:
            response = requests.get(api_url, params={'per_page': 100})
            response.raise_for_status()
            contents = response.json()

            if not isinstance(contents, list):
                print(f"Error: Expected a list from API, but got {type(contents)}")
                return []

            page_states = [item['name'] for item in contents if item.get('type') == 'dir']
            all_state_names.extend(page_states)

            if 'next' in response.links:
                api_url = response.links['next']['url']
            else:
                api_url = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching directory contents from local Directory: {e}")

            local_path = os.path.join(config.BASE_DIR, "STATES")
            state_list = [entry.name for entry in os.scandir(local_path) if entry.is_dir()]
            print(state_list)
            return state_list
        except (KeyError, TypeError) as e:
            print(f"Error parsing GitHub API response: {e}")
            return []

    print(f"Successfully fetched a total of {len(all_state_names)} states.")
    return sorted(all_state_names)


@cache.memoize(timeout=3600)  # Cache for 1 hour
def load_geo(relative_file_path: str):

    local_path = os.path.join(config.BASE_DIR, relative_file_path)
    github_url = config.GITHUB_RAW_BASE_URL + relative_file_path.replace("\\", "/")

    if os.path.exists(local_path):
        print(f"Loading '{relative_file_path}' from local cache...")
        try:
            return gpd.read_file(local_path)
        except Exception as e:
            print(f"Error reading local file {local_path}: {e}")
            return None

    print(f"Local file not found. Attempting to download from: {github_url}")
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        response = requests.get(github_url, stream=True)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded and saved to '{local_path}'")

        return gpd.read_file(local_path)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from GitHub: {e}")

    return None