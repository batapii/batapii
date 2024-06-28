name: Update GitHub Profile

on:
  repository_dispatch:
    types: [test_trigger]
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'  # 6時間ごとに実行

permissions:
  contents: write
  packages: read
  pull-requests: write

concurrency: 
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  update-profile:
    name: Update Profile README and Metrics
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12.4'

      - name: Debug Information
        run: |
          echo "Python version:"
          python --version
          echo "Pip version:"
          pip --version
          echo "Contents of requirements.txt:"
          cat requirements.txt || echo "requirements.txt not found"
          echo "Available wakatime versions:"
          pip index versions wakatime
          echo "Repository contents:"
          ls -la
          echo "Searching for update_coding_stats.py:"
          find . -name update_coding_stats.py

      - name: Upgrade pip
        run: |
          python -m pip install --upgrade pip
          pip --version

      - name: Install dependencies
        run: |
          if [ -f "requirements.txt" ]; then
            echo "Installing from requirements.txt"
            pip install -r requirements.txt
          else
            echo "::error::requirements.txt not found"
            exit 1
          fi
          echo "Installed packages:"
          pip list

      - name: Update Coding Stats
        env:
          WAKATIME_API_KEY: ${{ secrets.WAKATIME_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: |
          if [ -f update_coding_stats.py ]; then
            python update_coding_stats.py
          else
            echo "::error::update_coding_stats.py not found"
            exit 1
          fi

      - name: Update recent GitHub activity
        uses: jamesgeorge007/github-activity-readme@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Update WakaTime stats
        uses: anmol098/waka-readme-stats@master
        with:
          WAKATIME_API_KEY: ${{ secrets.WAKATIME_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          SHOW_LINES_OF_CODE: "True"
          SHOW_PROFILE_VIEWS: "False"
          SHOW_COMMIT: "True"
          SHOW_DAYS_OF_WEEK: "True"
          SHOW_LANGUAGE: "True"
          SHOW_OS: "True"
          SHOW_PROJECTS: "True"
          SHOW_TIMEZONE: "True"
          SHOW_EDITORS: "True"
          SHOW_LANGUAGE_PER_REPO: "True"
          SHOW_SHORT_INFO: "True"
          SHOW_LOC_CHART: "True"

      - name: Update GitHub stats
        uses: lowlighter/metrics@latest
        with:
          token: ${{ secrets.GH_TOKEN }}
          plugin_lines: yes
          plugin_isocalendar: yes
          plugin_languages: yes
          plugin_achievements: yes
          plugin_notable: yes

      - name: Commit and push if changed
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "github-actions[bot]"
          git add README.md
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Update GitHub profile [skip ci]"
            git pull --rebase origin ${{ github.ref }}
            git push
          fi

      - name: Check for errors
        if: failure()
        run: |
          echo "::error::Workflow failed. Please check the logs for more information."
          exit 1
