# coding: utf-8
def hello():
    print("hello")
    
get_ipython().show_usage()
get_ipython().run_line_magic('pinfo', 'print')
get_ipython().run_line_magic('pinfo', 'socket')
import socket
get_ipython().run_line_magic('pinfo', 'socket')
socket.__file__
import pathlib
get_ipython().run_line_magic('pinfo2', 'pathlib.Path')
get_ipython().system('pwd')
get_ipython().system('cd ..')
get_ipython().run_line_magic('cd', '..')
get_ipython().run_line_magic('cd', '-')
get_ipython().system('ls')
data = get_ipython().getoutput('ls')
data
data
get_ipython().run_line_magic('ls', '')
get_ipython().run_line_magic('pwd', '')
get_ipython().system('pwd')
get_ipython().run_line_magic('cd', '~/')
get_ipython().run_line_magic('cd', '-')
path = get_ipython().getoutput('pwd')
path
lpath = get_ipython().run_line_magic('pwd', '')
lpath
type(path)
path.s
path.l
path.nlstr
path.spstr
get_ipython().run_line_magic('pinfo', 'path')
path.p
path.s
path.p[0].is_dir()
paths = get_ipython().getoutput('ls -l')
paths
paths.fields(0)
paths.fields(1)
paths.fields(2)
top
get_ipython().run_line_magic('top', '')
get_ipython().system('top')
paths
paths.grep(lambda x: x.startswith('l'), field=-1)
name = "Smital"
get_ipython().system('echo $name')
get_ipython().run_line_magic('quickref', '')
get_ipython().run_line_magic('quickref', '')
get_ipython().run_line_magic('whos', '')
get_ipython().run_line_magic('colors', 'Neutral')
asdfa
get_ipython().run_line_magic('colors', 'Linux')
get_ipython().run_line_magic('config', '')
get_ipython().run_line_magic('Config', 'TerminalInteractiveShell')
get_ipython().run_line_magic('config', 'TerminalInteractiveShell')
get_ipython().run_line_magic('pip', 'install requests')
get_ipython().run_line_magic('save', '')
get_ipython().run_line_magic('save', 'test.py')
def hello():
    print("hello")
    
get_ipython().run_line_magic('save', 'test.py')
def hello():
    print("hello")
    
get_ipython().run_line_magic('save', 'test.py')
get_ipython().run_line_magic('clear', '')
def hello():
    print("hello")
    
