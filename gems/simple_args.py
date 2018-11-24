# Copyright (c) 2018 Paul Reindell
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#############################################################
# Interface
#############################################################
from collections import namedtuple

# Command/Argument definition
Cmd = namedtuple('Command', 'desc cb args cmds', defaults=(None,None,None,None,))
Arg = namedtuple('Arg', 'name flags short desc default exmpl convert', defaults=(None,None,None,None,None,))

#Flags
OPTION   = 0  # simple 'flag' argument; example: '--foo' or '-f'
VALUE    = 1  # value argument;         example: '--foo=value' '-f=value'
UNNAMED  = 2  # unamed argument;        example; 'foo'
REQUIRED = 4  # required argument; omitting argument will print the help text

# print help
def print_help(cmd_name, cmd):
    _print_help(cmd, [cmd_name])

# execute command based on arguments
def exec_command(cmd_name, cmd, argv):
    return _execute_command(cmd, argv[1:], [cmd_name])

#############################################################
# Implementation
#############################################################
_PrintCmd = namedtuple('PrintCmd', 'name text desc cmds args mla_name mla_text mla_short')
_PrintArg = namedtuple('PrintArg', 'name text short desc')

_PRE_UNAMED = 0
_PRE_SHORT  = 1
_PRE_NAME   = 2

def _execute_command(cmd, argv, commands):
    help_args = ['help', '-help', '--help', '?']
    if (len(argv) == 0 and not cmd.cb) or (len(argv) > 0 and argv[0] in help_args):
        _print_help(cmd, commands)
        if len(argv) == 0:
            print('Error: Please specify Command!')
            print('')
            return -1
        return 0

    if cmd.cb:
        args = {}
        if cmd.args:
            for x in range(0, len(argv)):
                arg_name = argv[x]
                pre = _PRE_UNAMED
                if arg_name.find('--') == 0:
                    pre = _PRE_NAME
                elif arg_name.find('-') == 0:
                    pre = _PRE_SHORT

                found = False
                for arg in cmd.args:
                    cc = arg_name[pre:].split('=')
                    if (pre == _PRE_NAME and arg.name == cc[0]) or (pre == _PRE_SHORT and arg.short == cc[0]) or (pre == _PRE_UNAMED and arg.flags & UNNAMED and arg.name not in args):
                        found = True
                        if arg.flags & VALUE or pre == _PRE_UNAMED:
                            idx = 0 if pre == _PRE_UNAMED else 1
                            val = ''.join(cc[idx:]) if len(cc) > idx else ''
                            if val == '':
                                _print_help(cmd, commands)
                                print('Error: Argument \'{}\': Expects to have a value!'.format(arg.name))
                                if arg.flags & UNNAMED:
                                    print('  Example: {} <{}>'.format(' '.join(commands), arg.name))
                                else:
                                    print('  Example: {} --{}=<{}>'.format(' '.join(commands), arg.name, arg.exmpl if arg.exmpl else 'foo'))
                                print('')
                                return -1
                            v_str = val.strip('\'')
                            if arg.convert:
                                try:
                                    args[arg.name] = arg.convert(v_str)
                                except:
                                    _print_help(cmd, commands)
                                    print('Error: Argument \'{}\': Value not expected type!'.format(arg.name))
                                    if arg.exmpl:
                                        if arg.flags & UNNAMED:
                                            print('  Example: {} <{}>'.format(' '.join(commands), arg.exmpl))
                                        else:
                                            print('  Example: {} --{}=<{}>'.format(' '.join(commands), arg.name, arg.exmpl))
                                    print('')
                                    return -1
                            else:
                                args[arg.name] = v_str
                        else:
                            args[arg.name] = True
                        break
                if not found:
                    _print_help(cmd, commands)
                    print('Error: Argument \'{}\': Unknown Argument!'.format(arg_name))
                    print('')
                    return -1

            for arg in cmd.args:
                if not arg.name in args:
                    if arg.default is not None:
                        args[arg.name] = arg.default
                    elif arg.flags & REQUIRED:
                        _print_help(cmd, commands)
                        if arg.flags & UNNAMED:
                            print('Error: Argument \'{}\': Required Argument not set!'.format(arg.name))
                            print('  Example: {} <{}>'.format(' '.join(commands), arg.exmpl if arg.exmpl else arg.name))
                            print('')
                        else:
                            print('Error: Argument \'{}\': Required Argument not set!'.format(arg.name))
                            print('  Example: {} --{}=<{}>'.format(' '.join(commands), arg.name, arg.exmpl if arg.exmpl else 'foo'))
                            print('')
                        return -1
                    else:
                        args[arg.name] = None

        res = cmd.cb(args)
        return res if res else 0

    if cmd.cmds:
        if not argv[0] in cmd.cmds:
            _print_help(cmd, commands)
            print(' Error: Command \'{}\': Not a valid command!'.format(argv[0]))
            print('')
            return -1

        commands.append(argv[0])
        return _execute_command(cmd.cmds[argv[0]], argv[1:], commands)
    
    return -2

def _print_help(cmd, commands, pre_len=0, post_len=0):
    lines = []
    n = _collect_help(cmd, commands, 0, 0, lines, 0)
    for l in lines:
        print('{}{}'.format(l[0].ljust(n), ' : {}'.format(l[1]) if l[1] else ''))

def _collect_help(cmd, commands, pre_len, post_len, lines, n):
    if pre_len == 0:
        prefix = '   '
    else:
        prefix = ''.ljust(pre_len)

    names_args = []
    unamed_args = []
    arg_name_maxlen  = 0
    arg_text_maxlen  = 0
    arg_short_maxlen = 0

    if cmd.cb:
        if cmd.args:
            for arg in cmd.args:

                if arg.short:
                    arg_short = ' (-{})'.format(arg.short)
                else:
                    arg_short = ''

                if arg.flags & UNNAMED:
                    arg_text = '<{}>'.format(arg.name)
                else:
                    arg_text = '--{}{}'.format(arg.name, '=<{}>'.format(arg.exmpl if arg.exmpl else 'foo') if arg.flags & VALUE else '')

                if arg.default is not None:
                    arg_desc = '{} (default: {})'.format(arg.desc, arg.default)
                elif arg.flags & REQUIRED:
                    arg_desc = arg.desc
                else:
                    arg_desc = '{} (optional)'.format(arg.desc)
                
                l = len(arg_text)
                if l > arg_text_maxlen:
                    arg_text_maxlen = l

                l = len(arg_short)
                if l > arg_short_maxlen:
                    arg_short_maxlen = l

                l = len(arg.name)
                if l > arg_name_maxlen:
                    arg_name_maxlen = l

                pa = _PrintArg(
                    name=arg.name,
                    text=arg_text,
                    short=arg_short,
                    desc=arg_desc)

                if arg.flags & UNNAMED:
                    unamed_args.append(pa)
                else:
                    names_args.append(pa)

    cmd_text_maxlen = 0
    cmdlist = []
    if cmd.cmds:
        for cmd_name in cmd.cmds:
            cmdlist.append(cmd_name)
            l = len(cmd_name)
            if l > cmd_text_maxlen:
                cmd_text_maxlen = l

    if pre_len == 0:
        cmd_name = ' '.join(commands).ljust(post_len)
        #cmd_list_str = ' {{{}}}'.format('|'.join(cmdlist)) if cmd.cmds else ''
    else:
        cmd_name = commands[len(commands)-1].ljust(post_len)
        #cmd_list_str = ' <Command>' if cmd.cmds else ''


    cmd_text = '{}{}{}'.format(
        #cmd_list_str,
        ' <Command>'   if cmd.cmds             else '',
        ' <Arguments>' if len(unamed_args) > 0 else '',
        ' [Options]'   if len(names_args)  > 0 else '')

    cmd_desc = cmd.desc if cmd.desc else commands[len(commands)-1]
    if pre_len == 0:
        n = _add_line(lines, 'Usage:', None, n)

    n = _add_line(lines, '{}{}{}'.format(
        prefix,
        cmd_name,
        cmd_text),
        cmd_desc, n)

    if len(unamed_args) > 0 and pre_len == 0:
        n = _add_line(lines, '', None, n)
        n = _add_line(lines, 'Arguments:', None, n)

    for arg in unamed_args:
        n = _add_line(lines, '{}{}{}{}'.format(
            prefix,
            ''.ljust(post_len + 1),
            '{}'.format(arg.text).ljust(arg_text_maxlen), 
            '{}'.format(arg.short).ljust(arg_short_maxlen)),
            arg.desc if arg.desc else arg.name, n)
        
    if len(names_args) > 0 and pre_len == 0:
        n = _add_line(lines, '', None, n)
        n = _add_line(lines, 'Options:', None, n)

    names_args  = sorted(names_args,  key=lambda x: x.name)
    for arg in names_args:
        n = _add_line(lines, '{}{}{}{}'.format(
            prefix,
            ''.ljust(post_len + 1),
            '{}'.format(arg.text).ljust(arg_text_maxlen), 
            '{}'.format(arg.short).ljust(arg_short_maxlen)),
            arg.desc if arg.desc else arg.name, n)

    if cmd.cmds:
        if len(cmd.cmds) > 0 and pre_len == 0:
            pre_len = 3
            n = _add_line(lines, '', None, n)
            n = _add_line(lines, 'Commands:', None, n)
        else:
            pre_len = pre_len + len(cmd_name) + 1

        for cmd_name, cmd in cmd.cmds.items():
            n = _collect_help(cmd, commands + [cmd_name], pre_len, cmd_text_maxlen, lines, n)

        n = _add_line(lines, '', None, n)
        
    elif pre_len == 0:
        n = _add_line(lines, '', None, n)

    return n

def _add_line(lines, ll, lr, n):
    lines.append([ll, lr])
    return max(n, len(ll))
