import os
from github import Github

def main():
    token = os.getenv('GITHUB_TOKEN')
    target_issue_num = os.getenv('TARGET_ISSUE')
    repo_full_name = os.getenv('REPO_NAME')

    g = Github(token)
    repo = g.get_repo(repo_full_name)

    # Scenario A: Generate report for the specific issue just touched
    if target_issue_num:
        issue = repo.get_issue(number=int(target_issue_num))
        print(f"Generating report for issue #{issue.number}: {issue.title}")
        # ... logic to analyze issue and save report ...
    
    # Scenario B: Scan ALL issues (as per your request "read all the issues")
    else:
        print("Scanning all issues for report generation...")
        issues = repo.get_issues(state='all')
        for issue in issues:
            # ... logic to aggregate data ...
            pass

if __name__ == "__main__":
    main()
