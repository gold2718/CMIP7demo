import argparse
from github import Github, Auth
import os
from utils import last_actor

def parse_arguments():
    """Parses command-line input arguments using the argparse
    python module and outputs the final argument object.
    """

    # Create parser object:
    parser = argparse.ArgumentParser(description='Edits issues to add automated information.')

    #Add input arguments to be parsed:
    parser.add_argument('--access-token', metavar='<GITHUB_TOKEN>', action='store', type=str,
                        help="access token used to access GitHub API")

    parser.add_argument('--repo-name', metavar='<REPO_NAME>', action='store', type=str,
                        default="",
                        help="name of the repository that triggered this workflow")

    parser.add_argument('--issue-num', metavar='<ISSUE_NUMBER>', action='store', type=str,
                        default="",
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

    if not token:
        raise ValueError("Blank access token passed")
    # end if
    if not repo_name:
        raise ValueError("Blank repository name passed")
    # end if
    if not issue_number:
        raise ValueError("Blank issue number passed")
    # end if

#    token = Github.Auth.Token(os.getenv('GITHUB_TOKEN'))
#    repo_full_name = os.getenv('REPO_NAME')
#    issue_number = int(os.getenv('ISSUE_NUMBER'))

    try:
        ghub = Github(Auth.Token(token))
    except Exception as exc:
        raise ValueError(f"Error, could not create Github object from '{token}'\n{str(exc)}")
    # end try
    try:
        if '/' not in repo_name:
            repo_name = f"gold2718/{repo_name}"
        # end if
        repo = ghub.get_repo(repo_name)
    except Exception as exc:
        raise ValueError(f"Error, could not get repo from '{repo_name}'\n{str(exc)}")
    # end try
    try:
        issue = repo.get_issue(number=int(issue_number))
    except ValueError as verr:
        raise ValueError(f"Error, issue number, '{issue_number}', must be an integer")
    except Exception as exc:
        raise ValueError(f"Error, could not get issue from '{issue_number}'\n{str(exc)}")
    # end try

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
