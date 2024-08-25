from getpass import getpass
import bcrypt, json

pwd = getpass()
hash = bcrypt.hashpw(pwd.encode('ascii'), bcrypt.gensalt())

if bcrypt.checkpw(pwd.encode('ascii'), hash):
    print(hash.decode('ascii'))
    with open("config.json", "r") as f:
        cfg = json.loads(f.read())

    cfg["login"]["hash"] = hash.decode('ascii')

    with open("config.json", "w") as f:
        f.write(
            json.dumps(cfg, indent=4)
        )
        f.flush()

    print("[+] wrote to 'config.json'")
else:
    print('try again - password and hash did not match')