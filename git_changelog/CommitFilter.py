from git_changelog.Utils import match_any_pattern

class CommitFilter:
    "Filters commits according to rules set on creation"

    def __init__(self, message_filter=[], parents_filter=(0, float("inf"))):
        #TODO add author_filter, committer_filter and date_filter
        """
        message_filter is an iterable (e.g. list) of regexps used to exclude commits.
        parents_filter is a tuple of the form (min_parents, max_parents).
        """
        self.message_filter = message_filter

        try:
            if len(parents_filter) > 1:
                self.min_parents, self.max_parents = parents_filter
            else:
                raise ValueError("parents_filter must be a tuple of the form (min_parents, max_parents).")
        except TypeError as e:
            raise ValueError("parents_filter must be a tuple of the form (min_parents, max_parents).", e)

    
    def match(self, commit):
        """Filter by parents and then by commit message. Return True if matched"""

        # filter by parents
        try:
            if len(commit.parents) < self.min_parents or len(commit.parents) > self.max_parents:
                return True
        except AttributeError as e:
            raise ValueError("Commit object doesn't have parents atribute.", e)
        except TypeError as e:
            raise ValueError("Commit object has non-iterable parents atribute.", e)

        # filter by commit message
        try:
            if match_any_pattern(commit.message, self.message_filter):
                return True
        except AttributeError as e:
            raise ValueError("Commit object doesn't have message atribute.", e)

        return False

