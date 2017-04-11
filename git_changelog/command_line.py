import sys
from git_changelog.GitChangelog import append_to_changelog
from git_changelog.Logger import Logger, LOG_LEVELS
from git_changelog.Constants import EXIT_CODES


def main():
    try:
        append_to_changelog()
    except KeyboardInterrupt:
        Logger(LOG_LEVELS.ERROR).error("\nProgram interrupted by user")
        sys.exit(EXIT_CODES.CONTROL_C)
