import os
import json
import httpx
from github import Github
from datetime import datetime, timedelta
import re
import base64

GITHUB_TOKEN = os.environ["GH_TOKEN"]
WAKATIME_API_KEY = os.environ["WAKATIME_API_KEY"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)

def fetch_wakatime_stats():
    headers = {
        "Authorization": f"Basic {base64.b64encode(WAKATIME_API_KEY.encode()).decode()}"
    }
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    url = f"https://wakatime.com/api/v1/users/current/summaries?start={start_date}&end={end_date}"
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def format_github_data():
    user = g.get_user()
    contributions = sum(c.total for c in repo.get_stats_contributors() if c.author.login == user.login)
    private_repos = sum(1 for _ in user.get_repos(visibility='private'))
    
    return f"""<ul>
          <li>📦 {repo.size / 1024:.1f} kB Used in GitHub's Storage</li>
          <li>🏆 {contributions} Contributions in the Year {datetime.now().year}</li>
          <li>🚫 Not Opted to Hire</li>
          <li>📜 {user.public_repos} Public Repositories</li>
          <li>🔑 {private_repos} Private Repositories</li>
        </ul>"""

def format_commit_time(commits):
    total = sum(commits.values())
    return f"""<pre><code>🌞 Morning    {commits['morning']:3d} commits    {'█' * int(commits['morning']/total*8)}{'░' * (8-int(commits['morning']/total*8))} {commits['morning']/total*100:.2f}%
🌆 Daytime    {commits['daytime']:3d} commits    {'█' * int(commits['daytime']/total*8)}{'░' * (8-int(commits['daytime']/total*8))} {commits['daytime']/total*100:.2f}%
🌃 Evening    {commits['evening']:3d} commits    {'█' * int(commits['evening']/total*8)}{'░' * (8-int(commits['evening']/total*8))} {commits['evening']/total*100:.2f}%
🌙 Night      {commits['night']:3d} commits    {'█' * int(commits['night']/total*8)}{'░' * (8-int(commits['night']/total*8))} {commits['night']/total*100:.2f}%</code></pre>"""

def format_week_stats(commits):
    total = sum(commits.values())
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return "<pre><code>" + "\n".join([f"{day:<12} {commits[day.lower()]:3d} commits    {'█' * int(commits[day.lower()]/total*8)}{'░' * (8-int(commits[day.lower()]/total*8))} {commits[day.lower()]/total*100:.2f}%" for day in days]) + "</code></pre>"

def format_time_stats(stats):
    languages = stats["data"][0]["languages"]
    return "<pre><code>💬 Programming Languages: \n" + "\n".join([f"{lang['name']:<15} {lang['text']:<15} {'█' * int(lang['percent']/10)}{'░' * (10-int(lang['percent']/10))} {lang['percent']:.2f}%" for lang in languages[:5]]) + "</code></pre>"

def format_editors(stats):
    editors = stats["data"][0]["editors"]
    return "<pre><code>" + "\n".join([f"{editor['name']:<15} {editor['text']:<15} {'█' * int(editor['percent']/10)}{'░' * (10-int(editor['percent']/10))} {editor['percent']:.2f}%" for editor in editors]) + "</code></pre>"

def format_projects(stats):
    projects = stats["data"][0]["projects"]
    return "<pre><code>" + "\n".join([f"{project['name']:<15} {project['text']:<15} {'█' * int(project['percent']/10)}{'░' * (10-int(project['percent']/10))} {project['percent']:.2f}%" for project in projects[:5]]) + "</code></pre>"

def format_os(stats):
    operating_systems = stats["data"][0]["operating_systems"]
    return "<pre><code>" + "\n".join([f"{os['name']:<15} {os['text']:<15} {'█' * int(os['percent']/10)}{'░' * (10-int(os['percent']/10))} {os['percent']:.2f}%" for os in operating_systems]) + "</code></pre>"

def format_tech_stack():
    langs = repo.get_languages()
    total = sum(langs.values())
    return "<pre><code>" + "\n".join([f"{lang:<12} {count:2d} repos   {'█' * int(count/total*10)}{'░' * (10-int(count/total*10))} {count/total*100:.2f}%" for lang, count in langs.items()]) + "</code></pre>"

def update_readme_section(content, start_tag, end_tag):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    
    pattern = f"{start_tag}.*?{end_tag}"
    replacement = f"{start_tag}\n{content}\n{end_tag}"
    updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)

def get_commit_times():
    commits = repo.get_commits(author=g.get_user().login)
    times = {'morning': 0, 'daytime': 0, 'evening': 0, 'night': 0}
    for commit in commits:
        hour = commit.commit.author.date.hour
        if 6 <= hour < 12:
            times['morning'] += 1
        elif 12 <= hour < 18:
            times['daytime'] += 1
        elif 18 <= hour < 24:
            times['evening'] += 1
        else:
            times['night'] += 1
    return times

def get_week_stats():
    commits = repo.get_commits(author=g.get_user().login)
    days = {day.lower(): 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    for commit in commits:
        day = commit.commit.author.date.strftime("%A").lower()
        days[day] += 1
    return days

def main():
    try:
        wakatime_stats = fetch_wakatime_stats()
        
        update_readme_section(format_github_data(), "<!--START_SECTION:github-data-->", "<!--END_SECTION:github-data-->")
        update_readme_section(format_commit_time(get_commit_times()), "<!--START_SECTION:waka-commit-time-->", "<!--END_SECTION:waka-commit-time-->")
        update_readme_section(format_week_stats(get_week_stats()), "<!--START_SECTION:waka-week-stats-->", "<!--END_SECTION:waka-week-stats-->")
        update_readme_section(format_time_stats(wakatime_stats), "<!--START_SECTION:waka-time-stats-->", "<!--END_SECTION:waka-time-stats-->")
        update_readme_section(format_editors(wakatime_stats), "<!--START_SECTION:waka-editors-->", "<!--END_SECTION:waka-editors-->")
        update_readme_section(format_projects(wakatime_stats), "<!--START_SECTION:waka-projects-->", "<!--END_SECTION:waka-projects-->")
        update_readme_section(format_os(wakatime_stats), "<!--START_SECTION:waka-os-->", "<!--END_SECTION:waka-os-->")
        update_readme_section(format_tech_stack(), "<!--START_SECTION:waka-tech-stack-->", "<!--END_SECTION:waka-tech-stack-->")

        print("README updated successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
