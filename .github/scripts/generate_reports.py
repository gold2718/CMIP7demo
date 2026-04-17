import argparse
from github import Github
import os

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

    try:
        ghub = Github(Auth.Token(token))
    except Exception as exc:
        ghub = None
    # end try
    if not ghub:
        try:
            ghub = Github(token)
        except Exception as exc:
            raise ValueError(f"Error, could not create Github object from '{token}'\n{str(exc)}")
        # end try
    # end if
    try:
        if '/' not in repo_name:
            repo_name = f"gold2718/{repo_name}"
        # end if
        repo = ghub.get_repo(repo_name)
    except Exception as exc:
        raise ValueError(f"Error, could not get repo from '{repo_name}'\n{str(exc)}")
    # end try

    print("Scanning all issues for report generation...")
    issues = repo.get_issues(state='all')
    for issue in issues:
        # ... logic to aggregate data ...
        pass

if __name__ == "__main__":
    main()
