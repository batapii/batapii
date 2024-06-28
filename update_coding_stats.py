- name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests PyGithub

    - name: Debug Information
      run: |
        echo "Current directory: $(pwd)"
        echo "Directory contents:"
        ls -la
        echo "Python version:"
        python --version
        echo "Pip version:"
        pip --version
        echo "Installed packages:"
        pip list
    - name: Upgrade pip
        run: |
          python -m pip install --upgrade pip
          pip --version
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
      - name: Debug Python and pip
        run: |
          echo "Python version:"
          python --version
          echo "Pip version:"
          pip --version
          echo "Contents of requirements.txt:"
          cat requirements.txt || echo "requirements.txt not found"
          echo "Available wakatime versions:"
          pip index versions wakatime
          echo "Installed packages:"
          pip list
          echo "Searching for update_coding_stats.py:"
          find . -name update_coding_stats.py
          echo "Contents of update_coding_stats.py (if found):"
          cat update_coding_stats.py || echo "update_coding_stats.py not found"

    - name: Check for errors
      if: failure()
      run: |
        echo "::error::Workflow failed. Please check the logs for more information."
        exit 1
