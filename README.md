# python-gems

Collection of some python helper classes

## gems


#### simple_args.py
Simple but powerful argument parser. Supports named/unnamed arguments, options and hierarchical commands with clean help formatting.

Code Example:
```
import gems.simple_args as sa
import sys

def cmd_daemon_start(args):
	return 0

def cmd_daemon_stop(args):
	isForce = args['force']

def cmd_services_halt(args):
	service = args['service']
	seconds = args['wait']

cmds_daemon = {}
cmds_daemon['start'] = sa.Cmd(cb=cmd_daemon_start, desc='Starts Daemon')

cmds_daemon['stop']  = sa.Cmd(cb=cmd_daemon_stop,  desc='Stops Daemon', args=[
    sa.Arg(name='force', short='f', desc='force shutdown', flags=sa.OPTION) ])

cmds_service = {}
cmds_service['halt'] = sa.Cmd(cb=cmd_services_halt,    desc='Stops Service and halts it', args=[
    sa.Arg(name='service', desc='name of service', flags=sa.UNNAMED | sa.REQUIRED), 
    sa.Arg(name='wait', short='w', exmpl='seconds', desc='time to wait for service to be shutdown', flags=sa.VALUE, default=0, convert=int) ])

cmds = {}
cmds['daemon']  = sa.Cmd(cmds=cmds_daemon,  desc='Daemon manager')
cmds['service'] = sa.Cmd(cmds=cmds_service, desc='Daemon service manager')

cmd = sa.Cmd(cmds=cmds, desc='Management App')

res = sa.exec_command('simple_args_example', cmd, sys.argv)
```

Example Help:
```
$ python ./simple_args_example.py ?
 Usage:
    simple_args_example <Command>      : Management App
 
 Commands:
    daemon  <Command>                  : Daemon manager
            start                      : Starts Daemon
            stop  [Options]            : Stops Daemon
                  --force (-f)         : force shutdown (optional)
 
    service <Command>                  : Daemon service manager
            halt <Arguments> [Options] : Stops Service and halts it
                 <service>             : name of service
                 --wait=<seconds> (-w) : time to wait for service to be shutdown (default=0)
```

```
$ python ./simple_args_example.py daemon ?
 Usage:
    simple_args_example daemon <Command> : Daemon manager
 
 Commands:
    start                                : Starts Daemon
    stop  [Options]                      : Stops Daemon
          --force (-f)                   : force shutdown (optional)
```

```
$ python ./simple_args_example.py service halt ?
Usage:
   Manager service halt <Arguments> [Options] : Stops Service and halts it

Arguments:
    <service>                                 : name of service

Options:
    --wait=<seconds> (-w)                     : time to wait for service to be shutdown (default: 0)
```
