import argparse
from github import Github, Auth
import os
import re
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

class Case(dict):
    """Info for a NorESM experiment case"""

    __ex_compset_txt = "Experiment compset"
    __ex_grid_txt = "Experiment resolution (grid)"
    __ex_runtype_txt = "Experiment run type"
    __case_start_year_txt = "Case start year"
    __case_stop_year_txt = "Case stop year"
    __refcase_txt = "RUN_REFCASE"
    __refdate_txt = "RUN_REFDATE"
    __reftod_txt = "RUN_REFTOD"
    __tag_txt = "Source tag"
    __machine_txt = "Case machine"
    __project_txt = "Project number"

    __keywords = {__ex_compset_txt: "compset",
                  __ex_grid_txt: "resolution",
                  __ex_runtype_txt: "run_type",
                  __case_start_year_txt: "run_startyear",
                  __case_stop_year_txt: "run_stopyear",
                  __refcase_txt: "RUN_REFCASE",
                  __refdate_txt: "RUN_REFDATE",
                  __reftod_txt: "RUN_REFTOD",
                  __tag_txt: "SRC_TAG",
                  __machine_txt: "machine",
                  __project_txt: "project"}

    __case_path = {"Olivia": "/cluster/work/projects",
                   "Betzy": "/cluster/projects"}

    KEYWORDS = ["compset", "resolution", "run_type", "run_startyear",
                "run_stopyear", "RUN_REFCASE", "RUN_REFDATE", "RUN_REFTOD",
                "SRC_TAG", "machine", "project"]

    # The way a label looks when issue is created
    __label_init_re = re.compile(r"[#]{3} (.*)$")
    # The way a label looks after issue auto-processing
    __label_edit_re = re.compile(r"[*][*]([^:*]+):[*][*][ ](.*)$")
    # Find where bot comments start
    __bot_txt_re = re.compile(r"[>][ ]")

    def __init__(self, body):
        """Parse an issue body for experiment info"""
        super().__init__()
        self.__errors = []
        self.__bot_items = []
        need_value = False
        label_key = None
        line_num = 0
        for line in body.splitlines():
            line_num += 1
            line = line.strip()
            if not line:
                continue
            # end if

            if need_value:
                if label_key and (label_key in self):
                    self.add_error(f"Duplicate issue key, '{label_key}'",
                                   line_num)
                elif label_key:
                    self[label_key] = line.strip()
                    label_key = None
                else:
                    self.add_error("Missing issue key", line_num)
                # end if
                need_value = False
                continue
            # end if
            label = self.__label_init_re.match(line)
            if label is not None:
                label_txt = label.group(1)
                need_value = True
                if label_txt in self.__keywords:
                    label_key = self.__keywords[label_txt]
                else:
                    self.add_error("Unknown issue key", line_num)
                # end if
                continue
            # end if
            label = self.__label_edit_re.match(line)
            if label is not None:
                label_txt = label.group(1)
                label_value = label.group(2)
                if label_txt in self.__keywords:
                    label_key = self.__keywords[label_txt]
                else:
                    self.add_error("Unknown issue key", line_num)
                # end if
                if label_key and (label_key in self):
                    self.add_error(f"Duplicate issue key, '{label_key}'",
                                   line_num)
                elif label_key:
                    self[label_key] = label_value.strip()
                    label_key = None
                # end if (no else for now, could check label_value)
                continue
            # end if
            btext = self.__bot_txt_re.match(line)
            if btext:
                self.add_bot_text(btext.strip())
            # end if
        # end for

    def get_prop(self, prop_name):
        """Return a keyword property or None if not defined"""
        if prop_name in self:
            return self[prop_name]
        # end if
        return None

    def case_name(self):
        """Return a case name for this case or an error string"""
        compset = self.get_prop("compset")
        res = self.get_prop("resolution")
        start = self.get_prop("run_startyear")
        stop = self.get_prop("run_stopyear")
        if compset and res and start and stop:
#            compset = compset.split(':')[0]
            compset = str(type(compset))
            case_name = f"{compset}_{res}_{start}_{stop}"
        else:
            case_name = "ERROR: Missing case configuration items"
        # end if
        return case_name

    def case_path(self):
        """Return a case path for this case"""
        machine = self.get_prop("machine") or "<case_path_for_machine>"
        project = self.get_prop("project") or "<project>"
        if machine in Case.__case_path:
            cpath = Case.__case_path[machine]
        else:
            cpath = machine
        # end if
        return f"{cpath}/{project}/{self.case_name()}"


    def newcase_cmd(self):
        """Return a create_newcase command"""
        pass

    def new_body(self):
        """Assemble and return a new body text"""
        body_lines = []
        for key in self.KEYWORDS:
            if key in self:
                body_lines.append(f"**{key}**: {self[key]}")
            # end if
        # end for
        body_lines.append("")
        body_lines.extend(self.__bot_items)
        body_lines.extend(self.__errors)
        return "\n".join(body_lines)


    def add_bot_text(self, bot_text):
        """Add an item to the bot list"""
        self.__bot_items.append(f"> {bot_text}")

    def add_error(self, err_text, linenum):
        """Add an error to the body error list"""
        self.__errors.append(f"> **ERROR: {linenum}: {err_text}**")

    @property
    def num_errors(self):
        """Return the number of errors found"""
        return len(self.__errors)

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

# XXgoldyXX: v debug only
    print(f"XXG: Last committer: {last_committer}")
# XXgoldyXX: ^ debug only
    issue_case = Case(issue_body)
    if last_committer != "gold2718":
        # Example: Modify title and body
        case_name = issue_case.case_name()
        if case_name:
            new_title = case_name
        else:
            new_title = f"[ERRROS] {issue.title}"
        # end if
        new_body = f"{issue_case.new_body()}\n\n> *This issue was processed by the automation bot.*"

        # Edit the issue via API
        issue.edit(title=new_title, body=new_body)

        print(f"Updated issue #{issue_number}")

#===================================
if __name__ == "__main__":
    main()
