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

def last_actor(github, repo):
    """Find the GitHub ID of the last entity that modified an issue in
    <repo_name>"""
    last_actor = None
    last_issue = get_last_updated_issue(github, repo)

    if last_issue:
        last_issue.last_edited_by.login if last_issue.last_edited_by else 'Unknown'
        print(f"Issue #{last_issue.number}: {last_issue.title}")
        print(f"Last updated by: {last_actor}")
        print(f"Updated at: {last_issue.updated_at}")
    else:
        print("No issues found in this repository.")

        # Get all events/timeline for the issue
        timeline = issue.get_timeline()

        # Get the last event
        last_event = list(timeline)[-1]

        print(f"Last action by: {last_event.actor.login}")
        print(f"Action type: {last_event.event}")
    # end if
    return last_actor
