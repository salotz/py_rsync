from py_rsync import RsyncEndpoint, RsyncCommand, RsyncInfoOptions

src = RsyncEndpoint(path='/home/salotz', user='salotz', host='superior')
dest = RsyncEndpoint(path='/home/salotz/scratch', user='salotz', host='superior')

info = RsyncInfoOptions(('all', 'symsafe',))

command = RsyncCommand(
    src=src,
    dest=dest,
    includes=('help',),
    excludes=('your/path/to/excellence',),
)
print(command.render())
