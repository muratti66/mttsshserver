
### Command Filtered SSH Server Service 

#### - Feautures
- TTY supported
- Config file configuration support
- Multi-thread work
- All clients, commands and outputs can be logging
- No answer mode - no_answer
- Hold n seconds for first answer - sleep_between  
- Multi username-password support
- Only run the allowed commands - option 1
- Not running the denied commands - option 2

#### - Limits
- File copy not working
- Tunnel not working
- Only the user running the service can use.

#### - Requirements
- Python 3.x versions
- ssh-keygen for ssh server key generate
- Install the Python Requirements
- config.cfg edit for your specific usage. (allowed and denied commands, hostname, 
  banner, socket ip, port ..etc.)
- root privileges for running on port 22 (optional)

#### - Preparetion
~~~~ 
pip3 install -r requirements.txt
~~~~

~~~~
#_> mkdir key/
~~~~

~~~~
> #_> ssh-keygen -f key/ssh.key
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in key/ssh.key
Your public key has been saved in key/ssh.key.pub
The key fingerprint is:
SHA256:..................................
The key's randomart image is:
+---[RSA 3072]----+
 ..............................
+----[SHA256]-----+
~~~~
~~~~
#_> python3 main.py &
~~~~
~~~~
#_> tail -f mttSshServer.log
~~~~
#### with Python3 Paramiko Library (mttSshServer) - 2021