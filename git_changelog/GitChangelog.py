import os
import sys
import codecs
from glob import glob
from getopt import getopt, GetoptError
from git import Repo, InvalidGitRepositoryError
from git_changelog.Utils import match_any_pattern, max_by_lambda, ask_question, local_datetime
from git_changelog.Constants import EXIT_CODES, LOG_LEVELS, SKIP_COMMIT_PATTERNS
from git_changelog.Logger import Logger
from git_changelog import __version__


def parse_args():
    options = {
        "auto_commit": False,
        "detailed": False,
        "debug": False,
        "quiet": False,
        "skip_prompt": False,
        "version": "",
        "package_name": "",
        "changelog_path": "",
        "to_commit": "",
        "from_commit": "",
        "project_path": "",
        "urgency": "",
        "debian_branch": "",
        "user_name": "",
        "user_email": "",
    }

    try:
        opts, args = getopt(sys.argv[1:], "hvdqADY", [
            "help", "version", "debug", "auto-commit", "detailed", "yes",
            "project-path=", "next-version=", "package-name=", "changelog-path",
            "to-commit=", "from-commit=", "urgency=", "debian-branch=", "user-name=", "user-email="
        ])
        for o, a in opts:
            if o in ("-h", "--help"):
                Logger(LOG_LEVELS.INFO).info(
                    "Usage:\n"
                    "  changelog-git [options]\n"
                    "\n"
                    "Options:\n"
                    "  -h, --help                Show help.\n"
                    "  -v, --version             Show version.\n"
                    "  -d, --debug               Debug mode (print debug logs).\n"
                    "  -q, --quiet               Suppress all output (except errors).\n"
                    "  -A, --auto-commit         Create new branch and commit changelog.\n"
                    "  -D, --detailed            Do not skip guessed prompts.\n"
                    "  -Y, --yes                 Skip all prompts with defaults.\n"
                    "  --project-path=<path>     Path to project root (default current directory).\n"
                    "  --next-version=<version>  Set next changelog version (default ask in prompt).\n"
                    "  --package-name=<name>     Set package name (default ask in prompt).\n"
                    "  --changelog-path=<path>   Set relative changelog path (default 'debian/changelog').\n"
                    "  --to-commit=<ref>         Set to commit (default 'HEAD').\n"
                    "  --from-commit=<ref>       Set from commit (default last tag).\n"
                    "  --urgency=<name>          Set urgency (default from changelog).\n"
                    "  --debian-branch=<ref>     Set debian branch (default from changelog).\n"
                    "  --user-name=<name>        Set user name (default from git config).\n"
                    "  --user-email=<email>      Set user email (default from git config)."
                )
                sys.exit(0)
            if o in ("-v", "--version"):
                Logger(LOG_LEVELS.INFO).info("git_changelog: " + __version__)
                sys.exit(0)
            if o in ("-d", "--debug"):
                options["debug"] = True
            if o in ("-q", "--quiet"):
                options["quiet"] = True
            if o in ("-A", "--auto-commit"):
                options["auto_commit"] = True
            if o in ("-D", "--detailed"):
                options["detailed"] = True
            if o in ("-Y", "--yes"):
                options["skip_prompt"] = True
            if o == "--project-path":
                options["project_path"] = a
            if o == "--next-version":
                options["version"] = a
            if o == "--package-name":
                options["package_name"] = a
            if o == "--changelog-path":
                options["changelog_path"] = a
            if o == "--to-commit":
                options["to_commit"] = a
            if o == "--from-commit":
                options["from_commit"] = a
            if o == "--urgency":
                options["urgency"] = a
            if o == "--debian-branch":
                options["debian_branch"] = a
            if o == "--user-name":
                options["user_name"] = a
            if o == "--user-email":
                options["user_email"] = a

    except GetoptError, e:
        Logger(LOG_LEVELS.ERROR).error("changelog-git: Unknown option '%s'" % e.opt)
        sys.exit(EXIT_CODES.UNKNOWN_ARGUMENT)

    if options["debug"] and options["quiet"]:
        Logger(LOG_LEVELS.ERROR).error("changelog-git: -d/--debug and -q/--quiet can't be set in same time")
        sys.exit(EXIT_CODES.WRONG_ARGUMENTS)

    if options["skip_prompt"] and options["detailed"]:
        Logger(LOG_LEVELS.ERROR).error("changelog-git: -D/--detailed and -Y/--yes can't be set in same time")
        sys.exit(EXIT_CODES.WRONG_ARGUMENTS)

    return options


def setup_logger(options):
    if options["debug"]:
        return Logger(LOG_LEVELS.DEBUG)
    elif options["quiet"]:
        return Logger(LOG_LEVELS.ERROR)

    return Logger(LOG_LEVELS.INFO)


def set_project_path(options, git_logger):
    # set default project path
    default_project_path = os.getcwd()

    if options["project_path"]:
        project_path = options["project_path"]
    elif options["detailed"]:
        # ask project path
        project_path = os.path.abspath(
            ask_question("Project path (default %s): " % default_project_path, default_project_path)
        )
    else:
        git_logger.info("Project path: %s" % default_project_path)
        project_path = default_project_path
    git_logger.debug("project_path set to '%s'" % project_path)

    # check project path exist
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        git_logger.error("changelog-git: Can't find project directory '%s'" % project_path)
        sys.exit(EXIT_CODES.PROJECT_NOT_FOUND)
    os.chdir(project_path)
    git_logger.debug("chdir to project_path '%s'" % project_path)
    return project_path


def set_repo(project_path, git_logger):
    # check project has git
    try:
        repo = Repo(project_path)
        git_logger.debug("connecting to git repo")
    except InvalidGitRepositoryError, e:
        git_logger.error("changelog-git: Can't find git repo for '%s'" % e.message)
        sys.exit(EXIT_CODES.GIT_NOT_FOUND)

    # check git has commits
    try:
        repo.head.commit
    except ValueError:
        git_logger.error("changelog-git: Git has no commits")
        sys.exit(EXIT_CODES.GIT_NO_COMMITS)
    return repo


def set_changelog_path(options, git_logger):
    # set default changelog path
    changelog_files = glob("**/changelog")
    if len(changelog_files) > 0:
        default_changelog_path = changelog_files[0]
    else:
        default_changelog_path = "debian/changelog"

    if options["changelog_path"]:
        changelog_path = options["changelog_path"]
    elif options["detailed"]:
        # ask path to changelog
        changelog_path = ask_question(
            "Related path to changelog (default %s): " % default_changelog_path,
            default_changelog_path
        )
    else:
        git_logger.info("Related path to changelog: %s" % default_changelog_path)
        changelog_path = default_changelog_path
    git_logger.debug("set changelog_path to '%s" % changelog_path)

    # fails if changelog does not exist
    if os.path.isdir(changelog_path):
        git_logger.error("changelog-git: changelog '%s' is a directory" % changelog_path)
        sys.exit(EXIT_CODES.CHANGELOG_PATH_INVALID)
    changelog_path_dir = os.path.dirname(changelog_path)
    if not os.path.isdir(changelog_path_dir):
        git_logger.error("changelog-git: changelog dir '%s' doesn't exists" % changelog_path_dir)
        sys.exit(EXIT_CODES.CHANGELOG_PATH_INVALID)
    return changelog_path


def set_defaults(changelog_path, project_path, repo, git_logger):
    defaults = {}
    # set default package name and version
    if os.path.exists(changelog_path):
        git_logger.debug("changelog_path exists")
        with open(changelog_path, "r") as f:
            changelog_line = f.readline().split(" ")
    else:
        git_logger.debug("changelog_path doesn't exist")
        changelog_line = []

    if len(changelog_line) > 1:
        defaults["package_name"] = changelog_line[0]
        old_version = changelog_line[1].lstrip("(").rstrip(")")
        if old_version[-1] == "9":
            defaults["version"] = old_version[0:-1] + "10"
        else:
            defaults["version"] = old_version[0:-1] + chr(ord(old_version[-1]) + 1)
        defaults["debian_branch"] = changelog_line[2].rstrip(";")
        defaults["urgency"] = changelog_line[3].lstrip("urgency=").rstrip("\n")
    else:
        defaults["package_name"] = os.path.basename(project_path)
        defaults["version"] = "1.0"
        defaults["urgency"] = "low"
        defaults["debian_branch"] = "wheezy"

    # set default version from tag of HEAD commit if it is exist
    if len(repo.tags) > 0 and repo.git.rev_parse(repo.tags[0].commit) == repo.git.rev_parse(repo.head.commit):
        defaults["version"] = repo.tags[0]

    return defaults


def set_package_name(options, default, git_logger):
    if options["package_name"]:
        package_name = options["package_name"]
    elif options["detailed"]:
        # ask package name
        package_name = ask_question("Package name (default %s): " % default, default)
    else:
        git_logger.info("Package name: %s" % default)
        package_name = default
    git_logger.debug("set package_name to '%s" % package_name)
    return package_name


def set_version(options, default, git_logger):
    # ask version
    if options["version"]:
        version = options["version"]
    elif options["skip_prompt"]:
        git_logger.info("Version: %s" % default)
        version = default
    else:
        version = ask_question("Version (default %s): " % default, default)
    git_logger.debug("set version to '%s" % version)
    return version


def set_from_commit(options, git_logger, repo):
    if len(repo.tags) > 0:
        default = max_by_lambda(
            repo.tags,
            (lambda x: x.tag.tagged_date if x.tag else x.commit.committed_date)
        ).tag.tag
    else:
        default = "HEAD"

    if options["from_commit"]:
        from_rev = options["from_commit"]
    elif options["skip_prompt"]:
        git_logger.info("From commit: %s" % default)
        from_rev = default
    else:
        # ask from commit
        from_rev = repo.git.rev_parse(
            ask_question("From commit (default %s): " % default, default)
        )
    git_logger.debug("set from_rev to '%s" % from_rev)
    return from_rev


def set_to_commit(options, git_logger, repo):
    default = "HEAD"
    if options["to_commit"]:
        to_rev = options["to_commit"]
    elif options["detailed"]:
        # ask to commit
        to_rev = repo.git.rev_parse(
            ask_question("To commit (default %s): " % default, default)
        )
    else:
        git_logger.info("To commit: HEAD %s" % default)
        to_rev = default
    git_logger.debug("set to_rev to '%s" % to_rev)
    return to_rev


def commit_changelog(changelog_path, version, repo, git_logger):
    branch_name = "bump-%s" % version.replace("~", "-")
    git_logger.debug("create branch '%s' from HEAD" % branch_name)
    branch = repo.create_head(branch_name)
    git_logger.debug("checkout to branch '%s'" % branch_name)
    branch.checkout()
    git_logger.debug("add '%s' to index" % changelog_path)
    repo.index.add([changelog_path])
    commit_message = "bump %s\n\n[ci skip] [changelog skip]" % version
    git_logger.debug("commit with message:\n%s" % commit_message)
    repo.index.commit(commit_message)


def modify_changelog_file(path, text, git_logger):
    # append changelog
    if not os.path.exists(path):
        changelog_dir = os.path.dirname(path)
        if not os.path.exists(changelog_dir):
            os.makedirs(changelog_dir)
        open(path, "w+").close()
        git_logger.debug("create changelog '%s'" % path)
    with codecs.open(path, mode="r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(text + content)
    git_logger.debug("append changes to the top of changelog")


def generate_changelog(
        from_rev, to_rev, repo, package_name, version, debian_branch, urgency, name, email, current_time, git_logger
):
    changelog_template = "%s (%s) %s; urgency=%s\n%s\n -- %s <%s>  %s\n\n"
    log = generate_description(from_rev=from_rev, to_rev=to_rev, repo=repo)

    changelog_text = changelog_template % (
        package_name, version, debian_branch, urgency, log, name, email, current_time
    )
    git_logger.debug(changelog_text)
    return changelog_text


def generate_description(from_rev, to_rev, repo):
    if from_rev == to_rev:
        commits = [repo.commit(to_rev)]
    else:
        commits = list(repo.iter_commits("%s...%s" % (from_rev, to_rev)))
    included_commits = []
    for commit in commits:
        if not match_any_pattern(commit.message, SKIP_COMMIT_PATTERNS):
            included_commits.append(commit)

    return "\n".join([("  * %s" % commit.message.split("\n")[0]) for commit in included_commits])


def process():
    options = parse_args()
    git_logger = setup_logger(options)

    project_path = set_project_path(options, git_logger=git_logger)
    repo = set_repo(project_path, git_logger)
    changelog_path = set_changelog_path(options, git_logger=git_logger)
    defaults = set_defaults(changelog_path=changelog_path, project_path=project_path, git_logger=git_logger, repo=repo)
    package_name = set_package_name(options=options, default=defaults["package_name"], git_logger=git_logger)
    version = set_version(options=options, default=defaults["version"], git_logger=git_logger)
    to_rev = set_to_commit(options=options, git_logger=git_logger, repo=repo)
    from_rev = set_from_commit(options=options, git_logger=git_logger, repo=repo)

    # set urgency
    if options["urgency"]:
        urgency = options["urgency"]
    else:
        urgency = defaults["urgency"]
    git_logger.debug("set urgency to '%s" % urgency)

    # set debian_branch
    if options["debian_branch"]:
        debian_branch = options["debian_branch"]
    else:
        debian_branch = defaults["debian_branch"]
    git_logger.debug("set debian_branch to '%s" % debian_branch)

    # set current_time
    current_time = local_datetime().strftime("%a, %-d %b %Y %H:%M:%S %z")
    git_logger.debug("set current_time to '%s" % current_time)

    # set name
    if options["user_name"]:
        name = options["user_name"]
    else:
        name = repo.config_reader().get("user", "name")
    git_logger.debug("set name to '%s" % name)

    # set email
    if options["user_email"]:
        email = options["user_email"]
    else:
        email = repo.config_reader().get("user", "email")
    git_logger.debug("set email to '%s" % email)

    # generate changelog text
    changelog_text = generate_changelog(
        from_rev=from_rev,
        to_rev=to_rev,
        repo=repo,
        package_name=package_name,
        version=version,
        debian_branch=debian_branch,
        urgency=urgency,
        name=name,
        email=email,
        current_time=current_time,
        git_logger=git_logger
    )

    # append to changelog
    modify_changelog_file(changelog_path, changelog_text, git_logger=git_logger)

    # commit to new branch
    if options["auto_commit"]:
        commit_changelog(
            changelog_path=changelog_path,
            version=version,
            repo=repo,
            git_logger=git_logger
        )
