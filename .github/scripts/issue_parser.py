import argparse
from github import Github
import os
from utils import last_actor

def parse_arguments():
    """Parses command-line input arguments using the argparse
    python module and outputs the final argument object.
    """

    # Create parser object:
    parser = argparse.ArgumentParser(description='Edits issues to add automated information.')

    #Add input arguments to be parsed:
    parser.add_argument('--access_token', metavar='<GITHUB_TOKEN>', action='store', type=str,
                        help="access token used to access GitHub API")

    parser.add_argument('--repo-name', metavar='<REPO_NAME>', action='store', type=str,
                        help="name of the repository that triggered this workflow")

    parser.add_argument('--issue-num', metavar='<ISSUE_NUMBER>', action='store', type=str,
                        help="Number of issue that triggered this workflow")

    #Parse Argument inputs
    args = parser.parse_args()
    return args

def main():

    # Parse arguments
    args = parse_arguments()
    token = args.access_token
    issue_number = args.issue_num
    repo_name = args.repo_name

#    token = Github.Auth.Token(os.getenv('GITHUB_TOKEN'))
#    repo_full_name = os.getenv('REPO_NAME')
#    issue_number = int(os.getenv('ISSUE_NUMBER'))

    ghub = Github(token)
    repo = ghub.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    # Parse an issue
    issue_body = issue.body
    issue_title = issue.title
    last_committer = last_actor(ghub, repo)

    if last_actor != "gold2718":
        # Example: Modify title and body
        new_title = f"[Auto-Processed] {issue.title}"
        new_body = f"{issue.body}\n\n> *This issue was processed by the automation bot.*"

        # Edit the issue via API
        issue.edit(title=new_title, body=new_body)

        print(f"Updated issue #{issue_number}")

#===================================
if __name__ == "__main__":
    main()
