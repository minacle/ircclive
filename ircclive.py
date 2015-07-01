import sys
import urllib.request
import urllib.parse
import urllib.error
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
            print("[%s] disconnected." % (email, ))
            break
        else:
            d = json.loads(d.decode("utf-8"))
            if d["type"] == "oob_include":
                if oob_include(session, d["url"]):
                    print("[%s] connected successfully." % (email, ))
                else:
                    print("[%s] connection failed." % (email, ))
                break
            elif d["type"] == "stat_user":
                stat_user = d
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

def reconnect(session, cid):
    f = rpc_post(session, "reconnect", data=urllib.parse.urlencode({"session": session, "cid": cid}).encode("ascii"))
    d = json.loads(getresponse(f))

def _identify(clear=False):
    global email
    global password
    oe = email
    try:
        if clear:
            email = None
            password = None
        while not email:
            email = input("email: ")
        while not password:
            password = getpass.getpass("password: ")
    except KeyboardInterrupt:
        print("\n[%s] terminating..." % (oe or "(unknown)", ))
        sys.exit(0)

def _run():
    global stat_user
    while True:
        err = 0
        stat_user = None
        try:
            print("[%s] connecting..." % (email, ))
            stream(login(email, password, auth_formtoken()))
        except KeyboardInterrupt:
            print("\n[%s] terminating..." % (email, ))
            sys.exit(0)
        except urllib.error.HTTPError as e:
            err = e.code
        except:
            print()
            print("[%s]" % (email, ))
            traceback.print_exc()
            print()
        try:
            if stat_user:
                zombie = stat_user["limits"]["zombiehours"] * 60 - 10
                if zombie < 0:
                    zombie = 1430
                print("[%s] waiting for %d minutes..." % (email, zombie))
                time.sleep(zombie * 60)
            elif err == 400:
                print("[%s] bad request." % (email, ))
                _identify(True)
            elif err == 401:
                print("[%s] unauthorised." % (email, ))
                _identify(True)
            else:
                print("[%s] waiting for 90 seconds..." % (email, ))
                time.sleep(90)
        except KeyboardInterrupt:
            print("\n[%s] terminating..." % (email, ))
            sys.exit(0)

if __name__ == "__main__":
    email, password = None, None
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 1:
        email = sys.argv[1]
    _identify()
    _run()

# vim: ts=4 sts=4 sw=4 et

