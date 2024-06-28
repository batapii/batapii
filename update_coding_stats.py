import requests
import os
from github import Github
import base64

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
    repo_name = os.getenv('GITHUB_REPOSITORY')

    if not wakatime_api_key or not github_token or not repo_name:
        raise ValueError("必要な環境変数が設定されていません")

    try:
        # WakaTimeの統計データを取得
        stats = get_wakatime_stats(wakatime_api_key)
        total_time = stats['data']['grand_total']['text']

        # GitHubリポジトリを更新
        g = Github(github_token)
        repo = g.get_repo(repo_name)

        # README.mdを取得
        readme = repo.get_readme()
        content = base64.b64decode(readme.content).decode('utf-8')

        # 既存の統計情報を更新または新しい情報を追加
        stats_section = f"# Coding Stats\n\nTotal coding time last 7 days: {total_time}\n"
        if "# Coding Stats" in content:
            content = content.replace(content[content.index("# Coding Stats"):content.index("\n\n", content.index("# Coding Stats"))], stats_section)
        else:
            content += f"\n{stats_section}"

        # READMEを更新
        repo.update_file(readme.path, "Update coding stats", content, readme.sha)
        print("README updated with coding stats")

    except requests.exceptions.RequestException as e:
        print(f"WakaTime APIリクエストエラー: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    update_readme_with_stats()
