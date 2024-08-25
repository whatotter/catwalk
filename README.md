
<p align="center">
   <img src="./core/http/kitty/curious.png">

   <h1 align="center">catwalk-C²</h1>
</p>

<h4 align="center">CnC that supports dumb/TTY shells, plugins, remote file browsing and downloading, FW/IPS evasion, custom communication protocols, and more</h4>

## features
|     name      |description|
|---------------|-----------|
|multiplayer    |have multiple people control the same client at once, with their commands being echoed across all users|
|strong API     |REST API targeted towards ease of use and for use in scripts, plugins, etc.
|modularity     |extremely modular - add your own custom protocol/encryption, add web-controlled plugins, create stages to quickly run multiple commands
|auto-run stages|create stages using Jinja2 to run commands on a client with a couple of clicks, or just automatically run specific stages on connection
|`Ctrl+C`       |shells (using catwalk's payload) can reconnect if you hit ctrl+c - you are asked if you want to hit ctrl+c anyways ¯\\\_(ツ)_/¯
|evade FW/IPS   |evade firewalls/intrusion prevention systems by round-robining ports (using catwalk's payload)
|cross os       |catwalk can be ran anywhere, just need python3 and a few packages
|compatiblity   |you can use ncat, netcat, socat, custom shells, PTYs and non-PTYs, so on and so forth
|info harvesting|view clients' information at a glance; PC hostname, `whoami`, MAC address, OUI, and filter through them all
|remote file browsing|remotely view a client's files, traverse their file system and download files to the C2 that pique your interest

### feature comparison vs. pwncat
| | pwncat | catwalk |
|-|--------|---------|
|Scripting engine|✔️ PSE/Python|✔️ Jinja2|
|IPv4|✔️|✔️|
|IPv6|✔️|🛠️|
|Directory explorer|❌|✔️|
|||
|TCP|✔️|✔️|
|UDP|✔️|✔️|
|HTTP|✔️|🛠️|
|HTTPS|🛠️|🛠️|
|||
|Local PF|✔️|🛠️|
|Remote PF|✔️|🛠️|
|||
|Inbound port scan|✔️|❌|
|Outbound port scan|✔️|❌|
|Version detection|✔️|❌|
|||
|Chat|✔️|❌|
|Command Execution|✔️|✔️|
|Multiple Conns|❌|✔️|
|Allow/Deny|❌|❌|
|Re-accept|✔️|✔️|
|Self-injecting|✔️|✔️, stages|
|Port hopping|✔️|✔️|
|Emergency Shutdown|✔️|❌|
|Client info harvesting|❌|✔️|

> <sub>🛠️: Work in progress.</sub>  
> <sub></sub>  

<sub>as you can see, catwalk isn't too special</sub>

## install

1. install the required packages:  

   ```
   pip install flask requests flask-socketio
   ```

2. if you are using this in a real environment, run `genPassword.py` to generate a new password for the web interface:
   ```
   python3 genPassword.py
   ```

3. start the python script, with your bind IP address (0.0.0.0 for all):    
   ```
   python3 main.py 0.0.0.0
   ```

open your favorite browser, and navigate to `localhost:80`

## usage
on first access to the webpage, you will be shown a small interactive tutorial on how to use catwalk

## known issues
- interactive TTYs/PTYs are wonky sometimes

## disclaimer
This tool may be used for legal purposes only. Users take full responsibility for any actions performed using this tool. The author accepts no liability for damage caused by this tool. If these terms are not acceptable to you, then do not use this tool.

## contributing
yeah i'm gonna have to fill this out eventually
