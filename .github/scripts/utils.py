from github import Github

def get_last_updated_issue(ghubObj, repo):
    """Find the actor who made the last change to this repo's issues.
    Returns, the name of the last actor or none."""

    # Fetch issues sorted by 'updated' in descending order (newest first)
    # state='all' includes open, closed, and merged issues
    issues = repo.get_issues(state='open', sort='updated', direction='desc')

    # Get the first item (the most recently updated one)
    try:
        last_issue = issues[0]
    except StopIteration:
        last_issue = None
    # end try
    return last_issue

def last_actor(github, repo):
    """Find the GitHub ID of the last entity that modified an issue in
    <repo_name>"""
    last_actor = None
    last_issue = get_last_updated_issue(github, repo)

    if last_issue:
        printf(f"Github actor: {github.actor}")
        printf(f"Github triggering actor: {github.triggering_actor}")
        printf(f"event user login: {github.event.comment.user.login}")
        print(f"Issue #{last_issue.number}: {last_issue.title}")
        print(f"Updated at: {last_issue.updated_at}")
        print(f"Last updated by: {last_event.actor.login}")
        print(f"Action type: {last_event.event}")
    else:
        print("No issues found in this repository.")
    # end if
    return last_actor
