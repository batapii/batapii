import requests
import os
from github import Github
import base64
from datetime import datetime, timedelta
import json
import traceback
import re


api_key = os.getenv('WAKATIME_API_KEY')
github_token = os.getenv('GH_TOKEN')
repo_name = os.getenv('GITHUB_REPOSITORY')

def get_wakatime_stats(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    endpoints = {
        "weekly": "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        "annual": "https://wakatime.com/api/v1/users/current/stats/last_year",
    }
    
    results = {}
    for key, url in endpoints.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            results[key] = response.json()
            print(f"{key} データ取得成功")
        except requests.exceptions.RequestException as e:
            print(f"{key} データ取得エラー: {e}")
            results[key] = None
    
    return results

def format_time(seconds):
    return str(timedelta(seconds=seconds)).split('.')[0]

def calculate_peak_hours(weekly_stats):
    hourly_data = [0] * 24
    for day in weekly_stats['days']:
        for hour in day['hours']:
            hourly_data[hour['hour']] += hour['total_seconds']
    
    peak_start = hourly_data.index(max(hourly_data))
    peak_end = (peak_start + 4) % 24  # 4時間のピーク期間を仮定
    
    return f"{peak_start:02d}:00 - {peak_end:02d}:00"

def update_productivity_and_achievements(content, weekly_stats, annual_stats):
    total_time = weekly_stats['total_seconds']
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    peak_hours = calculate_peak_hours(weekly_stats)
    most_productive_day = max(weekly_stats['days'], key=lambda x: x['total_seconds'])['date']
    favorite_language = weekly_stats['languages'][0]['name']
    main_project = weekly_stats['projects'][0]['name']
    main_project_percent = weekly_stats['projects'][0]['percent']

    productivity_highlights = f"""<!--START_SECTION:productivity_highlights-->
<h2 align="center">🚀 Coding Productivity Highlights</h2>

- **Total Coding Time:** {total_hours} hrs {total_minutes} mins
- **Peak Coding Hours:** {peak_hours}
- **Most Productive Day:** {most_productive_day}
- **Favorite Language:** {favorite_language}
- **Main Project:** {main_project} ({main_project_percent:.2f}% of weekly time)
<!--END_SECTION:productivity_highlights-->
"""

    coding_achievements = f"""<!--START_SECTION:coding_achievements-->
<h2 align="center">🏆 Coding Achievements</h2>

- **Consistent Contributor:** {annual_stats['total_days_contributed']} days of coding in {datetime.now().year}
- **Language Diversity:** Proficient in {', '.join([lang['name'] for lang in weekly_stats['languages'][:3]])}
- **Project Dedication:** Over {weekly_stats['projects'][0]['hours']} hours spent on {main_project} this week
- **Tool Mastery:** Skilled in {', '.join([editor['name'] for editor in weekly_stats['editors'][:2]])}
<!--END_SECTION:coding_achievements-->
"""

    content = re.sub(r'<!--START_SECTION:productivity_highlights-->.*?<!--END_SECTION:productivity_highlights-->', 
                     productivity_highlights, content, flags=re.DOTALL)
    content = re.sub(r'<!--START_SECTION:coding_achievements-->.*?<!--END_SECTION:coding_achievements-->', 
                     coding_achievements, content, flags=re.DOTALL)

    return content

def update_readme_with_stats(repo, stats):
    if not all(stats.values()):
        print("一部のデータの取得に失敗しました。README更新をスキップします。")
        return

    readme = repo.get_readme()
    content = base64.b64decode(readme.content).decode('utf-8')
    
    weekly_stats = stats['weekly']['data']
    annual_stats = stats['annual']['data']
    
    # WakaTime統計セクションの更新
    waka_start = content.index("<!--START_SECTION:waka-->")
    waka_end = content.index("<!--END_SECTION:waka-->", waka_start)
    waka_stats = f"""<!--START_SECTION:waka-->
![Code Time](http://img.shields.io/badge/Code%20Time-{format_time(weekly_stats['total_seconds'])}-blue)

📊 **This Week I Spent My Time On** 

```text
💬 Programming Languages: 
{' '.join(f"{lang['name']:<20}{format_time(lang['total_seconds']):<15}{lang['percent']:.2f}%" for lang in weekly_stats['languages'][:5])}

🔥 Editors: 
{' '.join(f"{editor['name']:<20}{format_time(editor['total_seconds']):<15}{editor['percent']:.2f}%" for editor in weekly_stats['editors'])}

🐱‍💻 Projects: 
{' '.join(f"{proj['name']:<20}{format_time(proj['total_seconds']):<15}{proj['percent']:.2f}%" for proj in weekly_stats['projects'][:5])}

💻 Operating System: 
{' '.join(f"{os['name']:<20}{format_time(os['total_seconds']):<15}{os['percent']:.2f}%" for os in weekly_stats['operating_systems'])}
```

**I Mostly Code in {weekly_stats['languages'][0]['name']}** 

```text
{' '.join(f"{lang['name']:<20}{lang['text']:<15}{lang['percent']:.2f}%" for lang in weekly_stats['languages'][:5])}
```

Last Updated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC
<!--END_SECTION:waka-->
"""
    content = content[:waka_start] + waka_stats + content[waka_end + len("<!--END_SECTION:waka-->"):]
    
    # Productivity HighlightsとCoding Achievementsの更新
    content = update_productivity_and_achievements(content, weekly_stats, annual_stats)
    
    repo.update_file(readme.path, "Update coding stats", content, readme.sha)
    print("README updated with coding stats and achievements")

if __name__ == "__main__":
    wakatime_api_key = os.getenv('WAKATIME_API_KEY')
    github_token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    if not all([wakatime_api_key, github_token, repo_name]):
        raise ValueError("必要な環境変数が設定されていません")
    
    try:
        print("WakaTime統計の取得を開始します...")
        stats = get_wakatime_stats(wakatime_api_key)
        print("WakaTime統計の取得が完了しました")
        
        print("GitHubリポジトリへの接続を開始します...")
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        print("GitHubリポジトリへの接続が完了しました")
        
        print("READMEの更新を開始します...")
        update_readme_with_stats(repo, stats)
        print("READMEの更新が完了しました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print(f"詳細なエラー情報: {traceback.format_exc()}")
