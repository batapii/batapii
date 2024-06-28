import requests
import os
from github import Github
import base64
from datetime import datetime, timedelta

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

def update_readme_with_stats():
    wakatime_api_key = os.getenv('WAKATIME_API_KEY')
    github_token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    if not all([wakatime_api_key, github_token, repo_name]):
        raise ValueError("必要な環境変数が設定されていません")
    
    try:
        weekly_stats, annual_stats, projects, leaderboard = get_wakatime_stats(wakatime_api_key)
        
        # 統計情報の整形
        weekly_total = weekly_stats['data']['grand_total']['text']
        annual_total = format_time(annual_stats['data']['grand_total']['total_seconds'])
        top_languages = ", ".join([f"{lang['name']} ({lang['percent']}%)" for lang in weekly_stats['data']['languages'][:3]])
        top_projects = ", ".join([f"{proj['name']} ({format_time(proj['total_seconds'])})" for proj in projects['data'][:3]])
        leaderboard_rank = f"{leaderboard['data']['rank']} out of {leaderboard['data']['total_members']}"

        stats_section = f"""# Coding Stats

- 📅 Weekly Coding Time: {weekly_total}
- 🗓️ Annual Coding Time: {annual_total}
- 👨‍💻 Top Languages (Last 7 Days): {top_languages}
- 🚀 Top Projects: {top_projects}
- 🏆 Leaderboard Rank: {leaderboard_rank}

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # GitHubリポジトリを更新
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        readme = repo.get_readme()
        content = base64.b64decode(readme.content).decode('utf-8')

        if "# Coding Stats" in content:
            content = content.replace(content[content.index("# Coding Stats"):content.index("\n\n", content.index("# Coding Stats"))], stats_section)
        else:
            content += f"\n{stats_section}"

        repo.update_file(readme.path, "Update coding stats with premium features", content, readme.sha)
        print("README updated with premium coding stats")

    except requests.exceptions.RequestException as e:
        print(f"WakaTime APIリクエストエラー: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    update_readme_with_stats()
