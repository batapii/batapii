import os
import json
import httpx
from github import Github
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ["GH_TOKEN"]
WAKATIME_API_KEY = os.environ["WAKATIME_API_KEY"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

def fetch_wakatime_stats():
    headers = {
        "Authorization": f"Basic {WAKATIME_API_KEY}"
    }
    
    # Fetch last 7 days of coding activity
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    url = f"https://wakatime.com/api/v1/users/current/summaries?start={start_date}&end={end_date}"
    
    response = httpx.get(url, headers=headers)
    return response.json()

def update_readme_section(section_name, content):
    filename = f"README_{section_name}.md"
    with open(filename, "w") as f:
        f.write(content)

def format_time_stats(stats):
    languages = stats["data"][0]["languages"]
    formatted = "💬 Programming Languages:\n"
    for lang in languages[:5]:  # Top 5 languages
        percentage = lang["percent"]
        formatted += f"{lang['name']:<15} {lang['text_total_readable']:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_editors(stats):
    editors = stats["data"][0]["editors"]
    formatted = "🔥 Editors:\n"
    for editor in editors:
        percentage = editor["percent"]
        formatted += f"{editor['name']:<15} {editor['text_total_readable']:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_projects(stats):
    projects = stats["data"][0]["projects"]
    formatted = "🐱‍💻 Projects:\n"
    for project in projects:
        percentage = project["percent"]
        formatted += f"{project['name']:<15} {project['text_total_readable']:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def format_os(stats):
    operating_systems = stats["data"][0]["operating_systems"]
    formatted = "💻 Operating System:\n"
    for os in operating_systems:
        percentage = os["percent"]
        formatted += f"{os['name']:<15} {os['text_total_readable']:>15} {'■' * int(percentage/5)}{' ' * (20-int(percentage/5))} {percentage:.2f}%\n"
    return formatted

def main():
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
        readme = readme.replace(f"<!--START_SECTION:waka-{section}-->.*?<!--END_SECTION:waka-{section}-->",
                                f"<!--START_SECTION:waka-{section}-->\n{section_content}\n<!--END_SECTION:waka-{section}-->",
                                flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
