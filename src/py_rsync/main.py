import dataclasses as dc
import pkgutil
from pathlib import Path
from typing import (
    Optional,
    Tuple,
    Generator
)

from jinja2 import Template

__all__ = [
    'RSYNC_OPTIONS',
    'RSYNC_FLAGS',
    'RSYNC_INFO_OPTS',
    'RSYNC_KV_OPTS',
    'Endpoint',
    'InfoOptions',
    'Options',
    'Command',

]


RSYNC_OPTIONS = (
    # long, short, docstring
    ('dry-run', 'n', "perform a trial run with no changes made"),
    ('delete', None, "delete extraneous files from dest dirs"),
    ('delete-excluded', None, "also delete excluded files from dest dirs"),
    ('compress', 'z', "compress file data during the transfer"),
    ('update', 'u', "skip files that are newer on the receiver"),
    ('archive', 'a', "archive mode; equals -rlptgoD (no -H,-A,-X)"),
    ('verbose', 'v', "increase verbosity"),
    ('human-readable', 'h', "output numbers in a human-readable format"),
    ('itemize-changes', 'i', "output a change-summary for all updates"),
    ('stats', None, "give some file-transfer stats"),
    ('backup', 'b', "make backups (see --suffix & --backup-dir)"),
    ('suffix', None, "backup suffix (default ~ w/o --backup-dir)"),
)
"""The supported boolean flag options.

The long-name is canonical and will be validated for use. Use this
data structure to normalize names.

"""

RSYNC_FLAGS = (
    'dry-run',
    'delete',
    'delete-excluded',
    'compress',
    'update',
    'archive',
    'verbose',
    'human-readable',
    'itemize-changes',
    'stats',
    'backup',
)
"""Boolean options that require no explicit value. The presence implies 'True'"""

RSYNC_KV_OPTS = (
    'suffix',
)
"""The supported options that require typed values."""

RSYNC_INFO_OPTS = (
        'backup', # Mention files backed up
        'copy', # Mention files copied locally on the receiving side
        'del', # Mention deletions on the receiving side
        'flist1', # Mention file-list receiving/sending
        'flist2', # ?
        'misc1', # Mention miscellaneous information
        'misc2', # ?
        'mount', # Mention mounts that were found or skipped
        'updates', # Mention updated file/dir names
        'unchanged', # Mention unchanged names
        'progress-file', # Mention per-file progress
        'progress-total', # Mention total transfer progress
        'removed', # Mention files removed on the sending side
        'skipped', # Mention files that are skipped due to options used
        'stats1', # total data sent and speeds
        'stats2', # stats on files created, deleted, size, and number sent
        'stats3', # heap statistics on hosts
        'symsafe', # Mention symlinks that are unsafe

        # verbosity
        'all', # ALL4
        'vv', # ALL3 = $(ALL2) + BACKUP,MISC2,MOUNT,NAME2,REMOVE,SKIP
        'v', # ALL1 = COPY,DEL,FLIST,MISC,NAME,STATS,SYMSAFE
        'none', # ALL0
)
"""The specifiers for the 'info' option fields."""


@dc.dataclass
class InfoOptions():

    flags: Optional[ Tuple[str] ]

    def __iter__(self) -> Generator[str, None, None]:
        for f in self.flags:
            yield f

    def is_valid(self) -> bool:

        if len(self.flags) < 1:
            return False
        else:
            return True

@dc.dataclass
class Options():

    flags: Optional[ Tuple[str] ]
    includes: Optional[ Tuple[str] ]
    excludes: Optional[ Tuple[str] ]
    info: Optional[ InfoOptions ]

    # the key-value options
    suffix: str = '~'

    @staticmethod
    def is_flags_valid(flags):

        not_found = [True for _ in flags]
        for i, flag in enumerate(flags):
            if flag in RSYNC_FLAGS:
                not_found[i] = False

        if any(not_found):
            return False
        else:
            return True

    def is_valid(self):

        if not self.is_flags_valid(self.flags):
            return False

        elif not self.info.is_valid():
            return False

        else:
            return True

    def __post_init__(self):

        if not self.is_valid():
            raise ValueError("Invalid arguments")

    @staticmethod
    def normalize_flags(flags) -> Tuple[str]:

        flag_aliases = [(long_name, short_name)
                        for long_name, short_name, description
                        in RSYNC_FLAGS]

        # Just convert short names to long names, and raise an error
        # if it isn't recognized
        normalized_flags = []
        for flag in flags:

            alias_found = False
            for long_alias, short_alias in flag_aliases:

                if (flag == long_alias or
                    flag == short_alias):

                    normalized_flags.append(long_alias)
                    alias_found = True
                    break

            if not alias_found:
                raise ValueError(f"Flag '{flag}' not recognized or supported.")

        return tuple(normalized_flags)



@dc.dataclass
class Endpoint():

    path: Path
    user: Optional[str]
    host: Optional[str]


    def is_valid(self) -> bool:

        if self.path is None:
            return False

        elif (self.user is not None and
              self.host is None):
            return False

        else:
            return True

def get_rsync_template() -> str:
    """Load the template text for the rsync command."""

    path = "rsync_template/rsync_command.txt.j2"
    return pkgutil.get_data(__name__,
                            path)\
                  .decode()


@dc.dataclass
class Command():
    """Specifications for an rsync invocation."""

    src: Endpoint
    dest: Endpoint
    options: Optional[Options]

    def __post_init__(self) -> None:

        if not self.src.is_valid():
            raise ValueError("Invalid src endpoint")

        if not self.dest.is_valid():
            raise ValueError("Invalid dest endpoint")

    def render(self) -> str:

        d = {
            'flags' : self.options.flags,
            # TODO: Key-values
            'includes' : self.options.includes,
            'excludes' : self.options.excludes,
            'info' : self.options.info,
            'src' : self.src,
            'dest' : self.dest
        }

        template = Template(get_rsync_template())
        result = template.render(**d,
                                 trim_blocks=True,
                                 lstrip_blocks=True)

        return result

default_options = {
    'flags' : (
        'archive',
        'verbose',
        'human-readable', 'human-readable',
        'stats',
        'itemize-changes'
    ),

}
