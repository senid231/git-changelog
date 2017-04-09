if __name__ == "__main__":
    import os
    import sys
    from glob import glob
    from getopt import getopt, GetoptError
    from tzlocal import get_localzone
    from datetime import datetime
    from git import Repo, InvalidGitRepositoryError
    from Constants import EXIT_CODES, LOG_LEVELS
    from Logger import Logger

    git_logger = Logger(LOG_LEVELS.DEBUG)
    is_verbose = False

    def if_empty(value, default):
        return value if value != "" else default

    # change working directory if -C argument specified
    try:
        opts, args = getopt(sys.argv[1:], "C:V")
        for o, a in opts:
            if o == "-C":
                os.chdir(a)
            if o == '-V':
                is_verbose = True
    except GetoptError, e:
        git_logger.error("Unknown option '%s'" % e.opt)
        sys.exit(EXIT_CODES.UNKNOWN_ARGUMENT)

    try:
        # set default project path
        default_project_path = os.getcwd()

        if is_verbose:
            # ask project path
            result = raw_input("Project path (default %s): " % default_project_path)
            project_path = os.path.abspath(if_empty(result, default_project_path))
        else:
            git_logger.info("Project path: %s" % default_project_path)
            project_path = default_project_path

        # check project path exist
        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            git_logger.error("Can't find project directory '%s'" % project_path)
            sys.exit(EXIT_CODES.PROJECT_NOT_FOUND)
        os.chdir(project_path)

        # check project has git
        try:
            repo = Repo(project_path)
        except InvalidGitRepositoryError, e:
            git_logger.error("Can't find git repo for '%s'" % e.message)
            sys.exit(EXIT_CODES.GIT_NOT_FOUND)

        # check git has commits
        try:
            repo.head.commit
        except ValueError:
            git_logger.error("Git has no commits")
            sys.exit(EXIT_CODES.GIT_NO_COMMITS)

        # set default changelog path
        changelog_files = glob('**/changelog')
        if len(changelog_files) > 0:
            default_changelog_path = changelog_files[0]
        else:
            default_changelog_path = 'debian/changelog'  # TODO: from defaults

        if is_verbose:
            # ask path to changelog
            result = raw_input("Related path to changelog (default %s): " % default_changelog_path)
            changelog_path = if_empty(result, default_changelog_path)
        else:
            git_logger.info("Related path to changelog: %s" % default_changelog_path)
            changelog_path = default_changelog_path

        # create changelog if it does not exist
        if os.path.isdir(changelog_path):
            git_logger.error("changelog '%s' is a directory" % changelog_path)
            sys.exit(EXIT_CODES.CHANGELOG_PATH_INVALID)

        # set default package name and version
        with open(changelog_path, 'r') as f:
            changelog_line = f.readline().split(" ")
        if len(changelog_line) > 1:
            default_package_name = changelog_line[0]
            old_version = changelog_line[1][1:-1]
            if old_version[-1] == '9':
                default_version = old_version[0:-1] + '10'
            else:
                default_version = old_version[0:-1] + chr(ord(old_version[-1]) + 1)
        else:
            default_package_name = os.path.basename(project_path)
            default_version = "1.0"  # TODO: from defaults

        # set default to and from commit
        default_to_rev = repo.git.rev_parse(repo.head.commit)
        if len(repo.tags) > 1 and repo.git.rev_parse(repo.tags[0].commit) == default_to_rev:
            default_from_rev = repo.git.rev_parse(repo.tags[1].commit)
        else:
            default_from_rev = default_to_rev

        # set default rev from tag of HEAD commit if it is exist
        if len(repo.tags) > 0 and repo.git.rev_parse(repo.tags[0].commit) == repo.git.rev_parse(repo.head.commit):
            default_version = repo.tags[0]

        if is_verbose:
            # ask package name
            result = raw_input("Package name (default %s): " % default_package_name)
            package_name = if_empty(result, default_package_name)
        else:
            git_logger.info("Package name: %s" % default_package_name)
            package_name = default_package_name

        # ask version
        result = raw_input("Version (default %s): " % default_version)
        version = if_empty(result, default_version)

        # ask from commit
        result = raw_input("From commit (default HEAD %s): " % default_from_rev)
        from_rev = repo.git.rev_parse(if_empty(result, default_from_rev))

        if is_verbose:
            # ask to commit
            result = raw_input("To commit (default %s): " % default_to_rev)
            to_rev = repo.git.rev_parse(if_empty(result, default_to_rev))
        else:
            git_logger.info("To commit: HEAD %s" % default_to_rev)
            to_rev = default_to_rev

        # set urgency, debian branch, datetime TODO: from defaults
        urgency = "low"
        debian_branch = "wheezy"
        local_tz = get_localzone()
        current_time = datetime.now(tz=local_tz).strftime('%a, %-d %b %Y %H:%M:%S %z')

        # set email and name from git config
        name = repo.config_reader().get('user', 'name')
        email = repo.config_reader().get('user', 'email')

        # generate changelog text
        changelog_template = "%s (%s) %s; urgency=%s\n  * %s\n -- %s <%s>  %s\n\n"
        if from_rev == to_rev:
            commits = [repo.commit(to_rev)]
        else:
            commits = list(repo.iter_commits('%s...%s' % (from_rev, to_rev)))
        commits_to_remove = []
        for commit in commits:
            if commit.message.startswith("Merge branch") or commit.message.lstrip().startswith("bump"):
                commits_to_remove.append(commit)
        for commit_to_remove in commits_to_remove:
            commits.remove(commit_to_remove)
        log = "\n  * ".join([commit.message.rstrip("\n").split("\n")[0] for commit in commits])
        changelog_text = changelog_template % (
            package_name, version, debian_branch, urgency, log, name, email, current_time)
        git_logger.debug(changelog_text)

        # append changelog
        if not os.path.exists(changelog_path):
            os.makedirs(os.path.dirname(changelog_path))
            open(changelog_path, 'w+').close()
        with open(changelog_path, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(changelog_text + content)

    except KeyboardInterrupt:
        git_logger.error("\nProgram interrupted by user")
        sys.exit(EXIT_CODES.CONTROL_C)
