from py_rsync import (
    RsyncEndpoint,
    RsyncCommand,
    RsyncInfoOptions,
    RsyncOptions,
)

src = RsyncEndpoint(path='/home/salotz', user='salotz', host='superior')
dest = RsyncEndpoint(path='/home/salotz/scratch', user='salotz', host='superior')

info = RsyncInfoOptions(('all', 'symsafe',))

options = RsyncOptions(
    flags=('dry-run', 'compress', 'archive', 'verbose'),
    info=info,
    includes=('help',),
    excludes=('your/path/to/excellence',),
)

command = RsyncCommand(
    src=src,
    dest=dest,
    options=options
)
print(command.render())
