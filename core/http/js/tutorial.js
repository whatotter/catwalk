const viewportWidth = window.innerWidth;
const viewportHeight = window.innerHeight;

function getOffset(el) {
    const rect = document.getElementById(el).getBoundingClientRect();
    return {
      x: rect.left + window.scrollX,
      y: rect.top + window.scrollY,
      width: rect.width,
      height: rect.height
    };
  }

function zindex(el) {
    const elem = document.getElementById(el)

    if (elem.style.zIndex == "24") {
        elem.style.zIndex = "1"
    } else {
        elem.style.zIndex = "24"
    }
}

function setTutBoxXY(xy, desc, cat) {
    const tutbox = document.getElementById("tut-box")

    document.getElementById("tut-desc").innerHTML = desc

    document.getElementById("kitty").src = `/core/kitty/${cat}.png`
    if (cat == 'ty') {
        document.getElementById("kitty").height = 160
    }

    if (xy.width >= viewportWidth/1.5) {
        xy.y = xy.y - (tutbox.getBoundingClientRect().height)*1.1
    } else {
        if (xy.x >= viewportWidth/2) {
            xy.x = xy.x - xy.width - 8
        } else {
            xy.x = xy.x + xy.width + 8
        }
    }

    console.log(xy.y)
    console.log(viewportHeight)
    if (xy.y > viewportHeight/2) {
        window.scrollTo(0, xy.y-viewportHeight/2)
        xy.y = xy.y - (tutbox.getBoundingClientRect().height)/5
        console.log('scroll')
    }

    window.scrollTo(0, xy.y-viewportHeight/2)
    
    tutbox.style.left = `${xy.x}px`
    tutbox.style.top = `${xy.y}px`
}

const tutorialDone = localStorage.getItem("tutorial")
var isOk = false

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function clientdemo() {
    var xh = new XMLHttpRequest()
    xh.open("POST", "/api/host/dbg")
    xh.send(JSON.stringify(
        {"count": "2"}
    ))
}

async function doTutorial() {
    document.getElementById("tutorial-overlay").setAttribute("disabled", "false")

    const tutArray = [
        {"sidebar": ["this is the sidebar to quickly go through tabs", "ok"]},
        {"welcome-box": ["this is the welcome 'box' - here you can generate payloads pointing to this C2", "hurt"]},
        {"charts": ["these are charts that show information of currently connected clients - connection statuses, OUIs (Organizational Unique Identifier, identifies the vendor of a computer), operating systems", "sleep"]},
        {"listen-box": ["this is the listening box; it shows which protocol is listening on which IP and which port", "sleep"]},
        {"victims": ["this is where all connected clients will show up", "evil"]},
        {"plugins": ["here are where plugins will show up, and where you can read their descriptions and access them", "wall"]},
        {"tbox": ["this is the catwalk terminal - here you can manage victims and run a single command to multiple different hosts, etc.\n\ndon't be intimidated, it's real easy to use and either way you don't need to use it", "scared"]},
        
        {"dmo1": [0,0]}, // create fake clients
        
        {"victims": ["here should be 3 connected clients - they're not real, FYI :)", "surprised"]},
        {"charts": ["here you can see the charts in action - hover over them to see values", "confused"]},
        {"victims": ["press the button 'select' on any client of your choosing, then hit 'OK' here", "ok"]},
        {"victims": ["now hit delete on your keyboard! this should show a notification on the top right - hit delete again", "confused"]},
        {"victims": ["this deletes a client and blacklists them from connecting again with the same ID - don't worry, if you open a reverse shell with that client, they'll still be able to reconnect", "scared"]},
        {"tbox": ["here's the catwalk terminal - type help for a list of commands (who would've known)", "hurt"]},
        {"center": ["that concludes the end of the tutorial - thank you for downloading and using catwalk-c2!", "ty"]}
    ]

    for (var t=0; tutArray.length>t; t++) {

        var array = tutArray[t]
        var key = Object.keys(array)[0]
        var desc = array[key][0]
        var cat = array[key][1]
        document.getElementById("tut-click").disabled = false;

        if (key == "dmo1") {
            clientdemo()
            await sleep(500)
            continue
        } else if (key == "center") {
            setTutBoxXY(
                {x: (viewportWidth/2)-document.getElementById("tut-box").getBoundingClientRect().width/1.8, y: (viewportHeight/1.4), width:8, height:8},
                desc, cat
            )

            await sleep(10)
            document.getElementById("tutorial-overlay").scrollTop = document.getElementById("tut-box").offsetTop
            
            if (t == tutArray.length) {
                document.getElementById("tut-click").innerHTML = "finish"
            }
    
            while (!isOk) {
                await sleep(100)
            }
            isOk = false
            await sleep(100)

            continue
        }


        zindex(key)
        setTutBoxXY(
            getOffset(key),
            desc, cat
        )
        await sleep(10)
        document.getElementById("tutorial-overlay").scrollTop = document.getElementById("tut-box").offsetTop
        
        if (t == tutArray.length) {
            document.getElementById("tut-click").innerHTML = "finish"
        }

        while (!isOk) {
            await sleep(100)
        }
        isOk = false
        await sleep(100)
        zindex(key)

    }

    console.log("done")
    document.getElementById("tutorial-overlay").setAttribute("disabled", "true")
    localStorage.setItem("tutorial", "1")
}

document.addEventListener("DOMContentLoaded", async function(){
    document.getElementById("tut-click").addEventListener("mouseup", function(){
        isOk = true
    })

    if (tutorialDone == undefined) {
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: 'instant',
          })
        await doTutorial()
    }
})