import sys
import gems.simple_args as sa

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

cmd = sa.Cmd(cmds=cmds, desc='Example App')

res = sa.exec_command('simple_args_example', cmd, sys.argv)