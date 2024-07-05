import os
import json
import httpx
from github import Github
from datetime import datetime, timedelta
import re

GITHUB_TOKEN = os.environ["GH_TOKEN"]
WAKATIME_API_KEY = os.environ["WAKATIME_API_KEY"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

def fetch_wakatime_stats():
    headers = {
        "Authorization": f"Basic {WAKATIME_API_KEY}"
    }
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    url = f"https://wakatime.com/api/v1/users/current/summaries?start={start_date}&end={end_date}"
    
    response = httpx.get(url, headers=headers)
    response.raise_for_status()  # Will raise an exception for HTTP errors
    return response.json()

def update_readme_section(section_name, content):
    filename = f"README_{section_name}.md"
    with open(filename, "w") as f:
        f.write(content)

def format_time_stats(stats):
    languages = stats["data"][0]["languages"]
    formatted = "💬 Programming Languages:\n"
    for lang in languages[:5]:  # Top 5 languages
        name = lang.get('name', 'Unknown')
        total_time = lang.get('total_seconds', 0)
        hours, remainder = divmod(total_time, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"
        percentage = lang.get('percent', 0)
        formatted += f"{name:<15} {time_str:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_editors(stats):
    editors = stats["data"][0].get("editors", [])
    formatted = "🔥 Editors:\n"
    for editor in editors:
        name = editor.get('name', 'Unknown')
        total_time = editor.get('total_seconds', 0)
        hours, remainder = divmod(total_time, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"
        percentage = editor.get('percent', 0)
        formatted += f"{name:<15} {time_str:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_projects(stats):
    projects = stats["data"][0].get("projects", [])
    formatted = "🐱‍💻 Projects:\n"
    for project in projects:
        name = project.get('name', 'Unknown')
        total_time = project.get('total_seconds', 0)
        hours, remainder = divmod(total_time, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"
        percentage = project.get('percent', 0)
        formatted += f"{name:<15} {time_str:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_os(stats):
    operating_systems = stats["data"][0].get("operating_systems", [])
    formatted = "💻 Operating System:\n"
    for os in operating_systems:
        name = os.get('name', 'Unknown')
        total_time = os.get('total_seconds', 0)
        hours, remainder = divmod(total_time, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m"
        percentage = os.get('percent', 0)
        formatted += f"{name:<15} {time_str:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def main():
    try:
        stats = fetch_wakatime_stats()
        
        update_readme_section("time_stats", format_time_stats(stats))
        update_readme_section("editors", format_editors(stats))
        update_readme_section("projects", format_projects(stats))
        update_readme_section("os", format_os(stats))

        # Update main README.md
        with open("README.md", "r") as f:
            readme = f.read()

        for section in ["time_stats", "editors", "projects", "os"]:
            with open(f"README_{section}.md", "r") as f:
                section_content = f.read()
            readme = re.sub(f"<!--START_SECTION:waka-{section}-->.*?<!--END_SECTION:waka-{section}-->",
                            f"<!--START_SECTION:waka-{section}-->\n{section_content}\n<!--END_SECTION:waka-{section}-->",
                            readme, flags=re.DOTALL)

        with open("README.md", "w") as f:
            f.write(readme)

        print("README updated successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
