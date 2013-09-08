### JSS: python client for Jingdong Storage Service

For more detail for JSS , please visit (here)[http://man.jcloud.com/hosting/jss/index]

* Command-Line API
* Python API


### Command-Line  API
First set three environment variables :
```
export JSS_ACCESS_KEY=<Your-jss-access-key>
export JSS_SECRET_KEY=<Your-jss-secret-key>
export JSS_URL=<HOST-of-JSS-server>:<PORT-of-JSS-server>
```
Of course , you can add above to you `~/.bashrc` file, and then:
```
source ~/.bashrc
```
will make the same effects.

You'll find complete documentation on the shell by running `jss help`:
```shell
$ jss help 
usage: jss [--version] [--jss-access-key] [--jss-secret-key]
           [--jss-url JSS_URL]
           <subcommand> ...

Command-line interface to the Jindong Storage Service (JSS) API.

Positional arguments:
  <subcommand>
    bucket-create
    bucket-delete
    bucket-list
    object-delete
    object-get
    object-list
    object-put
    help             Display help about this program or one of its
                     subcommands.

Optional arguments:
  --version          show program's version number and exit
  --jss-access-key   Defaults to env[JSS_ACCESS_KEY].
  --jss-secret-key   Defaults to env[JSS_SECRET_KEY].
  --jss-url JSS_URL  Defaults to env[JSS_URL].

See "jss help COMMAND" for help on a specific command.
```


### Python API
There's also a complete Python API, but it has not yet been documented.

Quick-start using jss-client for python:
```python
>>> from jssclient import client 
>>> JSS_ACCESS_KEY='9c379f079214447fad2959c4621cd6feVb797oH1'     
>>> JSS_SECRET_KEY='5e998dbbafb44ca783099afcdead40fa7A3Vf7Fh'
>>> JSS_URL='192.168.195.63:6080'
>>> cl = client.Client(access_key=JSS_ACCESS_KEY, secret_key=JSS_SECRET_KEY, jss_url=JSS_URL) 
>>> cl.bucket_list() 
[...]
```
