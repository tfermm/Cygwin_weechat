from urllib.request import urlopen
from urllib.request import urlretrieve
import platform
from subprocess import call
import subprocess
import os

def get_cygwin_url():
    is_64_bit = platform.machine().endswith('64')

    if is_64_bit:
        url = "http://cygwin.com/setup-x86_64.exe"
    else:
        url = "http://cygwin.com/setup-x86.exe"
    return url

def download_file(url):
    file_name = url.split('/')[-1]
    u = urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(u.headers['Content-Length'])

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = "%10d  [%3.2f%%]" % (file_size_dl, (file_size_dl * 100.00 / file_size))
        print (status,)
        
    f.close()
    return file_name
def install_cygwin(file_path, file_name):
    command = file_name + " -B -R \"" + file_path + "\\cygwin\" -q -n -s http://cygwin.mirrorcatalogs.com -P wget,tar,vim,weechat,weechat-python,openssl,openssh,mintty,dos2unix"
    subprocess.call(command, shell=True)

def patch_cygwin_portable(path):
    f = open('cygwin/Cygwin.bat','w')
    f.write('@echo off\n')
    f.write('FOR /F "tokens=* USEBACKQ" %%F IN (`echo %cd%`) DO (\n')
    f.write('	SET dir=%%F\n')
    f.write(')\n')
    f.write('chdir "%CD%/bin"\n')
    f.write('start "" "mintty.exe" -\n')
    f.close()

def auto_start_weechat_patch():
    f = open('cygwin/etc/skel/.bash_profile','w')

    print('if [ -f "${HOME}/.bashrc" ] ; then', end="",file=f)
    print('\n  source "${HOME}/.bashrc"', end="",file=f)
    print('\nfi', end="",file=f)
    print('\nif [ -f weechat.py ]; then', end="",file=f)
    print('\n    py weechat.py', end="",file=f)
    print('\nfi', end="",file=f)
    print('\nrm weechat.python', end="",file=f)
    print('\nweechat', end="",file=f)
    f.close()
    
    command="start cygwin/bin/dos2unix.exe cygwin/etc/skel/.bash_profile"
    subprocess.call(command, shell=True)
	
def generate_weechat_python():
    f = open('cygwin/etc/skel/weechat.py','w')
    print("import os", end="", file=f)
    print("\nif not os.path.exists('.weechat'):", end="", file=f)
    print("\n    os.mkdir('.weechat')", end="", file=f)
    print("\nif not os.path.exists('.weechat/python'):", end="", file=f)
    print("\n    os.mkdir('.weechat/python')", end="", file=f)
    print("\nif not os.path.exists('.weechat/python/autoload'):", end="", file=f)
    print("\n    os.mkdir('.weechat/python/autoload')", end="", file=f)
    print("\nf = open('.weechat/python/autoload/setup.py','w+')", end="", file=f)
    print("\nf.write('import weechat\\n')", end="", file=f)
    print("\nf.write('weechat.register(\"test_python\", \"FlashCode\", \"1.0\", \"GPL3\", \"Test script\", \"\", \"\")\\n')\n", end="", file=f)
    f.close()
    
def add_server(serverName, username, port, serverAddress, isssl, autoconnect):
    f = open('cygwin/etc/skel/weechat.py','a')
    print("\n", end="", file=f)
    if isssl:
        print("f.write('weechat.command(\"\", \"/server add " + serverName + " " + serverAddress + "/" + str(port) + " -ssl\")\\n')\n", end="", file=f)
        print("f.write('weechat.command(\"\", \"/set irc.server." + serverName + ".ssl_verify off\")\\n')\n", end="", file=f)
    else:
        print("f.write('weechat.command(\"\", \"/server add " + serverName + " " + serverAddress + "/" + str(port) + "\")\\n')\n", end="", file=f)
    if autoconnect:
       print("f.write('weechat.command(\"\", \"/set irc.server." + serverName + ".autoconnect on\")\\n')\n", end="", file=f) 
    print("f.write('weechat.command(\"\", \"/set irc.server." + serverName + ".nicks \\'" + username + "," + username + "2," + username + "3," + username + "4," + username + "5\\'\")\\n')\n", end="", file=f)
    print("f.write('weechat.command(\"\", \"/connect " + serverName + "\")\\n')\n", end="", file=f)
    f.close()


url = get_cygwin_url()
file_name = download_file(url)
file_path = os.path.dirname(os.path.realpath(__file__))

install_cygwin(file_path, file_name)

print("\nPatching Cygwin...\n")
patch_cygwin_portable(file_path + "\\cygwin")
auto_start_weechat_patch()
print("\nDone")

print("Setting up weechat")
generate_weechat_python()

done = False
while done == False:
    if done == False:
        try:
            count = int(input("How many irc servers would you like to add: "))
            for i in range(count):
                username = input("Your username: ")
                serverName = input("Server name: ")
                serverAddress = input("server address: ")
                port = int(input("Server port(default is 6697): "))
                autoconnect = input("Autoconnect(y/n): ")
                isssl = input("Does this server use ssl(y/n): ")
                if isssl == "y" or isssl == "Y":
                    isssl = True
                else:
                    isssl = False
                if autoconnect == "y" or autoconnect == "Y":
                    autoconnect = True
                else:
                    autoconnect = False
                add_server(serverName, username, port, serverAddress, isssl, autoconnect)
            done = True
        except:
            print("You suck at inputting things")
command="start cygwin/bin/dos2unix.exe cygwin/etc/skel/weechat.py"
subprocess.call(command, shell=True)
