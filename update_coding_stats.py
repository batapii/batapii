import requests
import os
from github import Github
import base64
from datetime import datetime, timedelta
import json
import traceback
import re

print(f"WAKATIME_API_KEY set: {'WAKATIME_API_KEY' in os.environ}")
print(f"WAKATIME_API_KEY length: {len(os.environ.get('WAKATIME_API_KEY', ''))}")


api_key = os.getenv('WAKATIME_API_KEY')
github_token = os.getenv('GH_TOKEN')
repo_name = os.getenv('GITHUB_REPOSITORY')

print(f"WAKATIME_API_KEY set: {bool(api_key)}")
print(f"WAKATIME_API_KEY length: {len(api_key) if api_key else 'Not Set'}")
print(f"GH_TOKEN set: {bool(github_token)}")
print(f"GITHUB_REPOSITORY: {repo_name}")

if not api_key:
    raise ValueError("WAKATIME_API_KEYが設定されていません。")
if not github_token:
    raise ValueError("GH_TOKENが設定されていません。")
if not repo_name:
    raise ValueError("GITHUB_REPOSITORYが設定されていません。")


encoded_key = base64.b64encode(api_key.encode()).decode()
print(f"Encoded API Key: {encoded_key}")

def get_wakatime_stats(api_key):
    headers = {
        "Authorization": "Basic " + encoded_key
    }

    
    response = requests.get("https://api.wakatime.com/api/v1/users/current/stats/last_7_days", headers=headers)
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    if response.status_code == 401:
        print("認証エラー: 401 Unauthorized。APIキーを確認してください。")
    
    print(f"Authorization header: {headers['Authorization'][:15]}...{headers['Authorization'][-5:]}")

    # リーダーボードIDを設定（必要に応じて変更）
    leaderboard_id = "d9f9d9aa-ec93-4c1e-a82a-d8a77bb31a77"

    endpoints = {
        "weekly": "https://api.wakatime.com/api/v1/users/current/stats/last_7_days",
        "annual": "https://api.wakatime.com/api/v1/users/current/stats/last_year",
        "projects": "https://api.wakatime.com/api/v1/users/current/projects",
        "leaderboard": f"https://api.wakatime.com/api/v1/users/current/leaderboards/{leaderboard_id}"
    }

    results = {}
    for key, url in endpoints.items():
        try:
            response = requests.get(url, headers=headers)
            print(response.json())
            response.raise_for_status()
            results[key] = response.json()
            print(f"{key} データ取得成功: {json.dumps(results[key], indent=2)[:500]}...")  # 最初の500文字のみ表示
        except requests.exceptions.HTTPError as e:
            print(f"{key} データ取得エラー: {e.response.status_code} {e.response.reason}")
            print(f"レスポンス内容: {e.response.text}")
            results[key] = None
        except requests.exceptions.RequestException as e:
            print(f"{key} データ取得中にエラーが発生しました: {e}")
            results[key] = None

    return results  # この行を関数内に正しく配置


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

def update_productivity_highlights(weekly_stats, annual_stats):
    total_time = weekly_stats['total_seconds']
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    peak_hours = calculate_peak_hours(weekly_stats)
    most_productive_day = max(weekly_stats['days'], key=lambda x: x['total_seconds'])['date']
    favorite_language = weekly_stats['languages'][0]['name']
    main_project = weekly_stats['projects'][0]['name']
    main_project_percent = weekly_stats['projects'][0]['percent']

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

- **Consistent Contributor:** {annual_stats['total_days_contributed']} days of coding in {datetime.now().year}
- **Language Diversity:** Proficient in {', '.join([lang['name'] for lang in weekly_stats['languages'][:3]])}
- **Project Dedication:** Over {weekly_stats['projects'][0]['hours']} hours spent on {weekly_stats['projects'][0]['name']} this week
- **Tool Mastery:** Skilled in {', '.join([editor['name'] for editor in weekly_stats['editors']])}
"""

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

![Lines of code](https://img.shields.io/badge/From%20Hello%20World%20I%27ve%20Written-{weekly_stats['lines_of_code']}%20lines%20of%20code-blue)

**🐱 My GitHub Data** 

> 📦 {(annual_stats['human_readable_total_size'])} Used in GitHub's Storage 
 > 
> 🏆 {annual_stats['human_readable_total_count']} Contributions in the Year {datetime.now().year}
 > 
> 🚫 Not Opted to Hire
 > 
> 📜 {len([repo for repo in repo.get_user().get_repos() if not repo.private])} Public Repositories 
 > 
> 🔑 {len([repo for repo in repo.get_user().get_repos() if repo.private])} Private Repositories 
 > 
**I'm an Early 🐤** 

```text
🌞 Morning    {sum(day['categories'][0]['total_seconds'] for day in weekly_stats['days'])} commits
🌆 Daytime    {sum(day['categories'][1]['total_seconds'] for day in weekly_stats['days'])} commits
🌃 Evening    {sum(day['categories'][2]['total_seconds'] for day in weekly_stats['days'])} commits
🌙 Night      {sum(day['categories'][3]['total_seconds'] for day in weekly_stats['days'])} commits
```
📅 **I'm Most Productive on {max(weekly_stats['days'], key=lambda x: x['total_seconds'])['date']}** 

```text
Monday       {weekly_stats['days'][0]['total_seconds']} commits
Tuesday      {weekly_stats['days'][1]['total_seconds']} commits
Wednesday    {weekly_stats['days'][2]['total_seconds']} commits
Thursday     {weekly_stats['days'][3]['total_seconds']} commits
Friday       {weekly_stats['days'][4]['total_seconds']} commits
Saturday     {weekly_stats['days'][5]['total_seconds']} commits
Sunday       {weekly_stats['days'][6]['total_seconds']} commits
```


📊 **This Week I Spent My Time On** 

```text
⌚︎ Time Zone: Asia/Tokyo

💬 Programming Languages: 
{' '.join(f"{lang['name']:<20}{format_time(lang['total_seconds']):<15}{lang['percent']:.2f}%" for lang in weekly_stats['languages'][:5])}

🔥 Editors: 
{' '.join(f"{editor['name']:<20}{format_time(editor['total_seconds']):<15}{editor['percent']:.2f}%" for editor in weekly_stats['editors'])}

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
