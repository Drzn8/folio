import os
import json
import requests

GITHUB_USERNAME = os.environ.get("PORTFOLIO_USERNAME", "Drzn8")
GITHUB_TOKEN = os.environ.get("CUSTOM_GITHUB_TOKEN")

def fetch_repositories():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=updated&per_page=100"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        repos = response.json()
        
        project_list = []
        for repo in repos:
            if not repo["fork"]:
                project_list.append({
                    "name": repo["name"],
                    "description": repo["description"] or "No description provided.",
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "language": repo["language"] or "Markdown/Text",
                    "updated_at": repo["updated_at"]
                })
                
        return project_list
    except Exception as e:
        print(f"Error gathering metadata from GitHub API: {e}")
        return None

def main():
    print(f"Querying public repositories for user: {GITHUB_USERNAME}...")
    projects = fetch_repositories()
    
    if projects is not None:
        output_path = "projects.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=4, ensure_ascii=False)
        print(f"Successfully compiled {len(projects)} repositories into {output_path}!")
    else:
        print("Execution halted due to upstream API faults.")

if __name__ == "__main__":
    main()