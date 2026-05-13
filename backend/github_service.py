import os
import httpx
from typing import Dict, Any

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_API_URL = "https://api.github.com"

async def exchange_code_for_token(code: str) -> str:
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("access_token")

async def get_user_repos(token: str):
    url = f"{GITHUB_API_URL}/user/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        # Fetching up to 100 repositories
        response = await client.get(url, headers=headers, params={"per_page": 100, "sort": "updated"})
        response.raise_for_status()
        return response.json()

async def get_repo_details(token: str, full_name: str):
    url = f"{GITHUB_API_URL}/repos/{full_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_repo_file_tree(token: str, full_name: str) -> list[str]:
    url = f"{GITHUB_API_URL}/repos/{full_name}/git/trees/HEAD"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params={"recursive": 1})
        if response.status_code != 200:
            return []
        tree_data = response.json()
        return [item['path'] for item in tree_data.get('tree', []) if item['type'] == 'blob']

async def analyze_tech_stack(token: str, full_name: str) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    primary_language = None
    frameworks = []
    has_docker = False
    
    async with httpx.AsyncClient() as client:
        # 1. Get primary language from languages endpoint
        lang_url = f"{GITHUB_API_URL}/repos/{full_name}/languages"
        lang_response = await client.get(lang_url, headers=headers)
        if lang_response.status_code == 200:
            languages = lang_response.json()
            if languages:
                # The first language is the most used
                primary_language = list(languages.keys())[0]

        # 2. Check root files for frameworks
        tree_url = f"{GITHUB_API_URL}/repos/{full_name}/git/trees/HEAD"
        tree_response = await client.get(tree_url, headers=headers)
        
        if tree_response.status_code == 200:
            tree_data = tree_response.json()
            files = [item['path'] for item in tree_data.get('tree', []) if item['type'] == 'blob']
            
            if 'Dockerfile' in files or 'docker-compose.yml' in files:
                has_docker = True
                
            # Analyze common package files
            # Note: A real implementation would fetch the contents of package.json/requirements.txt
            # and parse them to find precise dependencies (React, FastAPI, etc.)
            # For simplicity, we are guessing based on the files present or we can fetch them.
            
            if 'package.json' in files:
                # Fetch package.json content to detect frameworks
                content_url = f"{GITHUB_API_URL}/repos/{full_name}/contents/package.json"
                # To keep it simple without decoding base64 content in this implementation:
                frameworks.append("Node.js/JS") 
            
            if 'requirements.txt' in files or 'pyproject.toml' in files or 'setup.py' in files:
                frameworks.append("Python Framework")
            
            if 'pom.xml' in files or 'build.gradle' in files:
                frameworks.append("Java/JVM Framework")
                
            if 'go.mod' in files:
                frameworks.append("Go Modules")
                
            if 'Cargo.toml' in files:
                frameworks.append("Rust Cargo")

    return {
        "primary_language": primary_language,
        "frameworks": frameworks,
        "has_docker": has_docker
    }
