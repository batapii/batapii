import requests
import os
from github import Github
import base64
from datetime import datetime, timedelta
import json
import re

def get_wakatime_stats(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    endpoints = {
        "weekly": "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        "annual": "https://wakatime.com/api/v1/users/current/stats/last_year",
        "projects": "https://wakatime.com/api/v1/users/current/projects",
        "leaderboard": "https://wakatime.com/api/v1/users/current/leaderboards/"
    }
    
    results = {}
    for key, url in endpoints.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"{key} データ取得成功: {json.dumps(data, indent=2)[:500]}...")  # 最初の500文字のみ表示
            if 'data' not in data:
                print(f"警告: {key} データに 'data' キーがありません")
            results[key] = data
        except requests.exceptions.RequestException as e:
            print(f"{key} データ取得エラー: {e}")
            results[key] = None
    
    return results

def format_time(seconds):
    return str(timedelta(seconds=seconds)).split('.')[0]

def calculate_peak_hours(weekly_stats):
    hourly_data = [0] * 24
    for day in weekly_stats['data']['days']:
        for hour in day['hours']:
            hourly_data[hour['hour']] += hour['total_seconds']
    
    peak_start = hourly_data.index(max(hourly_data))
    peak_end = (peak_start + 4) % 24  # 4時間のピーク期間を仮定
    
    return f"{peak_start:02d}:00 - {peak_end:02d}:00"

def update_productivity_highlights(weekly_stats, annual_stats):
    total_time = weekly_stats['data']['total_seconds']
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    peak_hours = calculate_peak_hours(weekly_stats)
    most_productive_day = max(weekly_stats['data']['days'], key=lambda x: x['total_seconds'])['date']
    favorite_language = weekly_stats['data']['languages'][0]['name']
    main_project = weekly_stats['data']['projects'][0]['name']
    main_project_percent = weekly_stats['data']['projects'][0]['percent']

    return f"""
<h2 align="center">🚀 Coding Productivity Highlights</h2>

- **Total Coding Time:** {total_hours} hrs {total_minutes} mins
- **Peak Coding Hours:** {peak_hours}
- **Most Productive Day:** {most_productive_day}
- **Favorite Language:** {favorite_language}
- **Main Project:** {main_project} ({main_project_percent:.2f}% of weekly time)
"""

def update_coding_achievements(weekly_stats, annual_stats):
    return f"""
<h2 align="center">🏆 Coding Achievements</h2>

- **Consistent Contributor:** {annual_stats['data']['total_days_contributed']} days of coding in {datetime.now().year}
- **Language Diversity:** Proficient in {', '.join([lang['name'] for lang in weekly_stats['data']['languages'][:3]])}
- **Project Dedication:** Over {weekly_stats['data']['projects'][0]['hours']} hours spent on {weekly_stats['data']['projects'][0]['name']} this week
- **Tool Mastery:** Skilled in {', '.join([editor['name'] for editor in weekly_stats['data']['editors']])}
"""

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
    highlights = update_productivity_highlights(weekly_stats, annual_stats)
    achievements = update_coding_achievements(weekly_stats, annual_stats)

    content = re.sub(
        r'<h2 align="center">🚀 Coding Productivity Highlights</h2>.*?<h2 align="center">🏆 Coding Achievements</h2>',
        f'{highlights}\n{achievements}',
        content,
        flags=re.DOTALL
    )
    
    repo.update_file(readme.path, "Update coding stats with premium features", content, readme.sha)
    print("README updated with premium coding stats and new sections")

import traceback

if __name__ == "__main__":
    wakatime_api_key = os.getenv('WAKATIME_API_KEY')
    github_token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    if not all([wakatime_api_key, github_token, repo_name]):
        raise ValueError("必要な環境変数が設定されていません")
    
    try:
        print("WakaTime統計の取得を開始します...")
        weekly_stats, annual_stats, projects, leaderboard = get_wakatime_stats(wakatime_api_key)
        print("WakaTime統計の取得が完了しました")
        
        print("GitHubリポジトリへの接続を開始します...")
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        print("GitHubリポジトリへの接続が完了しました")
        
        print("READMEの更新を開始します...")
        update_readme_with_stats(repo, weekly_stats, annual_stats, projects, leaderboard)
        print("READMEの更新が完了しました")
    except requests.exceptions.RequestException as e:
        print(f"WakaTime APIリクエストエラー: {e}")
        print(f"詳細なエラー情報: {traceback.format_exc()}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print(f"詳細なエラー情報: {traceback.format_exc()}")
