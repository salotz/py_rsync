import dataclasses as dc
import pkgutil
from pathlib import Path
import typing as typ

from jinja2 import Template

__all__ = [
    'RsyncEndpoint',
    'RsyncInfoOptions',
    'RSYNC_INFO_OPTS',
    'RsyncCommand',
]


RSYNC_OPTS = (
    
)

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

@dc.dataclass
class RsyncEndpoint():

    path: Path
    user: str = None
    host: str = None


    def is_valid(self):

        if self.path is None:
            return False

        elif (self.user is not None and
              self.host is None):
            return False

        else:
            return True


@dc.dataclass
class RsyncInfoOptions():

    flags: typ.Tuple[bool] = ()

    def __iter__(self):
        for f in self.flags:
            yield f

    def is_valid(self):

        if len(self.flags) < 1:
            return False

def get_rsync_template():

    path = "rsync_template/rsync_command.txt.j2"
    return pkgutil.get_data(__name__,
                            path)\
                  .decode()

@dc.dataclass()
class RsyncCommand():
    """Specifications for an rsync invocation."""

    src: RsyncEndpoint
    dest: RsyncEndpoint
    info: RsyncInfoOptions = None
    includes: tuple = ()
    excludes: tuple = ()

    def __post_init__(self):

        if not self.src.is_valid():
            raise ValueError("Invalid src endpoint")

        if not self.dest.is_valid():
            raise ValueError("Invalid dest endpoint")


    def render(self):

        d = {
            'includes' : self.includes,
            'excludes' : self.excludes,
            'info' : self.info,
            'src' : self.src,
            'dest' : self.dest
        }

        template = Template(get_rsync_template())
        result = template.render(**d,
                                 trim_blocks=True,
                                 lstrip_blocks=True)

        return result


def gen_rsync_command(source_url, target_url,
                      includes=None, excludes=None,
                      dry=True,
                      delete=False,
                      delete_excluded=False,
                      compress=False,
                      safe=True,
                      force_update=False,):

    if includes is None:
        includes = []

    if excludes is None:
        excludes = []

    # make the strings for the command line invocation
    exclude_str = ' '.join([EXCLUDE_OPT_TEMPLATE.format(exclude)
                             for exclude in excludes])
    include_str = ' '.join([INCLUDE_OPT_TEMPLATE.format(include)
                             for include in includes])

    if dry:
        dry_str = '-n'
    else:
        dry_str = ''

    # if we have specified 1-way sync then delete files at the target,
    # we always delete excluded files
    if delete:
        delete_str = '--delete'
    else:
        delete_str = ''

    # if we are specifying to clean the target then delete the
    # excluded files, if not it will leave them alone like git and
    # cache stuff
    if delete_excluded:
        delete_excluded_str = '--delete-excluded'
    else:
        delete_excluded_str = ''


    if compress:
        compress_str = "-z"
    else:
        compress_str = ""

    # if we want the safe mode we set a backup and use the suffix '.rsync_backup'
    if safe:
        backup_str = "--backup --suffix='.rsync_backup'"
    else:
        backup_str = ""

    # if we are forcing update, don't update files that are newer on
    # receiver, the default mode is "safe" in the sense that if they
    # were modified those changes won't get overwritten. If you want
    # another "safe" option but still try to force, then use "safe"
    # option which makes backups
    if force_update:
        force_update_str = ""
    else:
        force_update_str = "--update"

    # make the CLI invocation
    command = RSYNC_RUN_TEMPLATE.format(
        exclude=exclude_str,
        include=include_str,
        source=source_url,
        target=target_url,
        dry=dry_str,
        delete=delete_str,
        delete_excluded=delete_excluded_str,
        info='',
        compress=compress_str,
        backup=backup_str,
        force_update=force_update_str,
    )

    return command
