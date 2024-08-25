# run(command:str, uuid:str, isASync:bool)
you can return `None` if the shell is in a queue (in cases where the shell isn't a 'stupid' shell)  
if it is a 'stupid' shell then you can just return the command output  
if the command is requested to be async then you can just return true  

e.g.  

|      | stupid shell         |smart shell  |
|------|----------------------|-------------|
|async |return `True`         |return `True`|
|normal|return command output |return `None`|