import requests
import os
from github import Github
import base64
from datetime import datetime, timedelta
import json

def get_wakatime_stats(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # 過去7日間の統計
    weekly_stats = requests.get("https://wakatime.com/api/v1/users/current/stats/last_7_days", headers=headers).json()
    
    # 年間の統計（プレミアム機能）
    annual_stats = requests.get("https://wakatime.com/api/v1/users/current/stats/last_year", headers=headers).json()
    
    # プロジェクト別の統計（プレミアム機能）
    projects = requests.get("https://wakatime.com/api/v1/users/current/projects", headers=headers).json()
    
    # リーダーボード情報（プレミアム機能）
    leaderboard = requests.get("https://wakatime.com/api/v1/users/current/leaderboards/", headers=headers).json()
    
    return weekly_stats, annual_stats, projects, leaderboard

def format_time(seconds):
    return str(timedelta(seconds=seconds)).split('.')[0]

def update_readme_content(weekly_stats, annual_stats, projects, leaderboard):
    total_time = weekly_stats['data']['total_seconds']
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    peak_hours = "10:00 AM - 2:00 PM"  # この部分は別途ロジックが必要
    most_productive_day = max(weekly_stats['data']['days'], key=lambda x: x['total_seconds'])['date']
    favorite_language = weekly_stats['data']['languages'][0]['name']
    main_project = weekly_stats['data']['projects'][0]['name']
    main_project_percent = weekly_stats['data']['projects'][0]['percent']

    productivity_highlights = f"""
<h2 align="center">🚀 Coding Productivity Highlights</h2>

- **Total Coding Time:** {total_hours} hrs {total_minutes} mins
- **Peak Coding Hours:** {peak_hours}
- **Most Productive Day:** {most_productive_day}
- **Favorite Language:** {favorite_language}
- **Main Project:** {main_project} ({main_project_percent:.2f}% of weekly time)
"""

    coding_achievements = f"""
<h2 align="center">🏆 Coding Achievements</h2>

- **Consistent Contributor:** {weekly_stats['data']['days_including_holidays']} days of coding in the last week
- **Language Diversity:** Proficient in {', '.join([lang['name'] for lang in weekly_stats['data']['languages'][:3]])}
- **Project Dedication:** Over {weekly_stats['data']['projects'][0]['hours']} hours spent on {main_project} this week
- **Tool Mastery:** Skilled in {', '.join([editor['name'] for editor in weekly_stats['data']['editors']])}
"""

    return productivity_highlights + coding_achievements

def update_readme_with_stats(repo, weekly_stats, annual_stats, projects, leaderboard):
    readme = repo.get_readme()
    content = base64.b64decode(readme.content).decode('utf-8')
    
    # WakaTime統計セクションの更新
    waka_start = content.index("<!--START_SECTION:waka-->")
    waka_end = content.index("<!--END_SECTION:waka-->", waka_start)
    waka_stats = f"""<!--START_SECTION:waka-->
![Code Time](http://img.shields.io/badge/Code%20Time-{format_time(weekly_stats['data']['total_seconds'])}-blue)

![Profile Views](http://img.shields.io/badge/Profile%20Views-{weekly_stats['data']['user_profile_views']}-blue)

![Lines of code](https://img.shields.io/badge/From%20Hello%20World%20I%27ve%20Written-{weekly_stats['data']['lines_of_code']}%20lines%20of%20code-blue)

**🐱 My GitHub Data** 

> 📦 {(annual_stats['data']['human_readable_total_size'])} Used in GitHub's Storage 
 > 
> 🏆 {annual_stats['data']['human_readable_total_count']} Contributions in the Year {datetime.now().year}
 > 
> 🚫 Not Opted to Hire
 > 
> 📜 {len([repo for repo in repo.get_user().get_repos() if not repo.private])} Public Repositories 
 > 
> 🔑 {len([repo for repo in repo.get_user().get_repos() if repo.private])} Private Repositories 
 > 
**I'm an Early 🐤** 

```text
🌞 Morning    {sum(day['categories'][0]['total_seconds'] for day in weekly_stats['data']['days'])} commits
🌆 Daytime    {sum(day['categories'][1]['total_seconds'] for day in weekly_stats['data']['days'])} commits
🌃 Evening    {sum(day['categories'][2]['total_seconds'] for day in weekly_stats['data']['days'])} commits
🌙 Night      {sum(day['categories'][3]['total_seconds'] for day in weekly_stats['data']['days'])} commits
```
📅 **I'm Most Productive on {max(weekly_stats['data']['days'], key=lambda x: x['total_seconds'])['date']}** 

```text
Monday       {weekly_stats['data']['days'][0]['total_seconds']} commits
Tuesday      {weekly_stats['data']['days'][1]['total_seconds']} commits
Wednesday    {weekly_stats['data']['days'][2]['total_seconds']} commits
Thursday     {weekly_stats['data']['days'][3]['total_seconds']} commits
Friday       {weekly_stats['data']['days'][4]['total_seconds']} commits
Saturday     {weekly_stats['data']['days'][5]['total_seconds']} commits
Sunday       {weekly_stats['data']['days'][6]['total_seconds']} commits
```


📊 **This Week I Spent My Time On** 

```text
⌚︎ Time Zone: Asia/Tokyo

💬 Programming Languages: 
{' '.join(f"{lang['name']:<20}{format_time(lang['total_seconds']):<15}{lang['percent']:.2f}%" for lang in weekly_stats['data']['languages'][:5])}

🔥 Editors: 
{' '.join(f"{editor['name']:<20}{format_time(editor['total_seconds']):<15}{editor['percent']:.2f}%" for editor in weekly_stats['data']['editors'])}

💻 Operating System: 
{' '.join(f"{os['name']:<20}{format_time(os['total_seconds']):<15}{os['percent']:.2f}%" for os in weekly_stats['data']['operating_systems'])}
```

**I Mostly Code in {weekly_stats['data']['languages'][0]['name']}** 

```text
{' '.join(f"{lang['name']:<20}{lang['text']:<15}{lang['percent']:.2f}%" for lang in weekly_stats['data']['languages'][:5])}
```

Last Updated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC
<!--END_SECTION:waka-->
"""
    content = content[:waka_start] + waka_stats + content[waka_end + len("<!--END_SECTION:waka-->"):]
    
    # 新しい統計セクションの更新
    new_stats = update_readme_content(weekly_stats, annual_stats, projects, leaderboard)
    highlight_start = content.index('<h2 align="center">🚀 Coding Productivity Highlights</h2>')
    achievement_end = content.index('</h2>', content.index('<h2 align="center">🏆 Coding Achievements</h2>')) + 5
    content = content[:highlight_start] + new_stats + content[achievement_end:]
    
    repo.update_file(readme.path, "Update coding stats with premium features", content, readme.sha)
    print("README updated with premium coding stats and new sections")

if __name__ == "__main__":
    wakatime_api_key = os.getenv('WAKATIME_API_KEY')
    github_token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    if not all([wakatime_api_key, github_token, repo_name]):
        raise ValueError("必要な環境変数が設定されていません")
    
    try:
        weekly_stats, annual_stats, projects, leaderboard = get_wakatime_stats(wakatime_api_key)
        
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        update_readme_with_stats(repo, weekly_stats, annual_stats, projects, leaderboard)
    except requests.exceptions.RequestException as e:
        print(f"WakaTime APIリクエストエラー: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
