// /api/data/plugins

var plugArray = []
var plgremovedMsg = false
var plugcontainer = document.getElementById('plugtainer');

function createPlugin(name, value) {
    // Create the main div element
    const tinyBox = document.createElement('div');

    if (value["endpoint"][0] != "/") {
        value["endpoint"] = "/"+value["endpoint"]
    }

    tinyBox.classList.add('tiny-box');
    tinyBox.classList.add('pluginbox');
    tinyBox.id = name+"_PDIV"

    const bigDiv = document.createElement('div');
    bigDiv.style.cssText = 'float:left; padding-top: 1px; padding-right: 1px; width: 100%; height: 90%';

    // Create the first inner div element with float:right style
    const innerDiv1 = document.createElement('div');
    innerDiv1.style.cssText = 'float:right; padding-top: 1px; padding-right: 1px;';

    // Create the h2 element
    const h2Element = document.createElement('h2');
    h2Element.textContent = name;

    // Create the span elements
    const descSpan = document.createElement('span');
    descSpan.textContent = value['desc'];

    const epSpan = document.createElement('span');
    epSpan.textContent = `Sends you to: ${value["endpoint"]}`;

    // Create the button element
    const buttonElement = document.createElement('button');
    buttonElement.classList.add('connect-button');
    buttonElement.textContent = 'Open';
    buttonElement.addEventListener('click', function() {
        location.href = "/plugin?n="+name
    });

    // Append elements to their respective parent elements
    bigDiv.appendChild(innerDiv1);
    bigDiv.appendChild(h2Element);
    bigDiv.appendChild(descSpan);

    bigDiv.appendChild(document.createElement('br'));
    bigDiv.appendChild(document.createElement('br'));

    bigDiv.appendChild(epSpan)

    bigDiv.appendChild(document.createElement('br'));

    tinyBox.append(bigDiv)

    bigDiv.appendChild(document.createElement('br'));

    tinyBox.appendChild(buttonElement);

    if (value["buttons"] != undefined) {
        for (var i=0; i<Object.keys(value["buttons"]).length; i++) {
            key = Object.keys(value["buttons"])[i]
            val = value["buttons"][key]
    
            if (val == undefined) { continue }
    
            var customButton = document.createElement('button');
            customButton.classList.add('connect-button');
            customButton.classList.add('mtop');
            customButton.textContent = key;
            customButton.addEventListener('click', function() {
                var apiCall = new XMLHttpRequest();
                apiCall.open('GET', "/plugins"+val, true);
                apiCall.send()
            });
    
            tinyBox.appendChild(document.createElement('br'));
            tinyBox.appendChild(customButton)
        }
    }


    // Return the created div
    return tinyBox;
}

function updatePlugins() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/api/data/plugins', true);
    xhr.onload = function() {
        var jsonData = JSON.parse(xhr.responseText)

        if (Object.keys(jsonData).includes("failure")) {
            if (jsonData["failure"] == "login") {
                window.location = "/login"
            }
        }
        
        if (Object.keys(jsonData).length >= 1 && plgremovedMsg == false) {
            document.getElementById("plugtainer").removeChild(document.getElementById("plug-message"))
            plgremovedMsg = true
        } else if (Object.keys(jsonData).length == 1 && plgremovedMsg == false) {
            document.getElementById("plug-message").innerHTML = "no plugins :("
        }
        
        for (var i=0; i<Object.keys(jsonData).length; i++) {
            var key = Object.keys(jsonData)[i]
            var val = jsonData[key]

            plugArray.push(key)
            plugcontainer.appendChild(createPlugin(key, val));
        }
    };

    xhr.send();
}

document.addEventListener("DOMContentLoaded", function(){
    plugcontainer = document.getElementById('plugtainer');
    updatePlugins()
})