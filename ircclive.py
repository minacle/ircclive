import sys
import urllib.request
import urllib.parse
import json
import time
import getpass
import io
import gzip
import traceback

baseurl = "https://www.irccloud.com/chat/"
stat_user = None

def rpc(method, path, session=None, token=None, keepalive=False, data=None):
    r = urllib.request.Request(urllib.parse.urljoin(baseurl, path), method=method)
    r.add_header("User-Agent", "IRCCLive")
    if method == "POST":
        r.add_header("Content-Type","application/x-www-form-urlencoded")
    if session:
        r.add_header("Cookie", "session=" + session)
    if keepalive:
        r.add_header("Connection", "keep-alive")
    if token:
        r.add_header("x-auth-formtoken", token)
    return urllib.request.urlopen(r, data)

def rpc_get(session, path, keepalive=False):
    return rpc("GET", path, session, keepalive=keepalive)

def rpc_post(session, path, keepalive=False, data=None):
    return rpc("POST", path, session, keepalive=keepalive, data=data)

def getresponse(response):
    b = io.BytesIO()
    b.write(response.read())
    b.seek(0, 0)
    if response.info().get("Content-Encoding") == "gzip":
        f = gzip.GzipFile(fileobj=b)
        return f.read().decode("utf-8")
    else:
        return b.read().decode("utf-8")

def auth_formtoken():
    f = rpc("POST", "auth-formtoken", data=b"")
    d = json.loads(getresponse(f))
    if d.get("success", False):
        return d["token"]
    return None

def login(email, password, token):
    f = rpc("POST", "login", token=token, data=urllib.parse.urlencode({"email": email, "password": password, "token": token}).encode("ascii"))
    d = json.loads(getresponse(f))
    if d.get("success", False):
        return d["session"]
    return None

def stream(session):
    f = rpc_get(session, "stream", True)
    global stat_user
    interval = 0
    while True:
        d = f.readline()
        if not d:
            print("[" + email + "] " + "disconnected.")
            break
        else:
            d = json.loads(d.decode("utf-8"))
            if d["type"] == "oob_include":
                if oob_include(session, d["url"]):
                    print("[" + email + "] " + "connected successfully.")
                else:
                    print("[" + email + "] " + "connection failed.")
                    break
            elif d["type"] == "stat_user":
                stat_user = d
            elif d["type"] == "idle":
                heartbeat(session)
            elif d["type"] == "buffer_msg":
                interval += 1
                if interval >= 10:
                    heartbeat(session)
                    interval = 0
    try:
        f.close()
    except:
        pass

def oob_include(session, url):
    f = rpc_get(session, url)
    d = json.loads(getresponse(f))
    for i in d:
        if i["type"] == "makeserver":
            if i["disconnected"]:
                reconnect(session, i["cid"])
    return True if d else False

def heartbeat(session):
    f = rpc_post(session, "heartbeat", data=urllib.parse.urlencode({"session": session, "selectedBuffer": stat_user.get("last_selected_bid", -1)}).encode("ascii"))
    d = json.loads(getresponse(f))

def reconnect(session, cid):
    f = rpc_post(session, "reconnect", data=urllib.parse.urlencode({"session": session, "cid": cid}).encode("ascii"))
    d = json.loads(getresponse(f))

def _run():
    while True:
        try:
            print("[" + email + "] " + "connecting...")
            stream(login(email, password, auth_formtoken()))
        except KeyboardInterrupt:
            print("[" + email + "] " + "terminating...")
            break
        except:
            print()
            print("[" + email + "]")
            traceback.print_exc()
            print()
        print("[" + email + "] " + "waiting for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    email, password = None, None
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if not email:
        email = input("email: ")
    if not password:
        password = getpass.getpass("password: ")
    _run()
