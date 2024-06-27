import requests
import os
from github import Github

def get_wakatime_stats(api_key):
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_readme_with_stats():
    wakatime_api_key = os.getenv('WAKATIME_API_KEY')
    github_token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')  # 形式: ユーザー名/リポジトリ名

    if not wakatime_api_key or not github_token or not repo_name:
        raise ValueError("必要な環境変数が設定されていません")

    # WakaTimeの統計データを取得
    stats = get_wakatime_stats(wakatime_api_key)
    total_time = stats['data']['grand_total']['text']

    # GitHubリポジトリを更新
    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # README.mdを更新
    readme = repo.get_readme()
    new_content = f"# Coding Stats\n\nTotal coding time last 7 days: {total_time}\n"
    repo.update_file(readme.path, "Update coding stats", new_content, readme.sha)

    print("README updated with coding stats")

if __name__ == "__main__":
    update_readme_with_stats()
