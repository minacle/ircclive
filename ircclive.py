import sys
import urllib.request
import urllib.parse
import json
import time

def auth_formtoken():
    f = urllib.request.urlopen(urllib.request.Request("https://www.irccloud.com/chat/auth-formtoken", data=b"", method="POST"))
    d = json.loads(f.read().decode("ascii"))
    if d.get("success", False):
        return d["token"]
    return None

def login(email, password, token):
    r = urllib.request.Request("https://www.irccloud.com/chat/login", data=urllib.parse.urlencode({"email": email, "password": password, "token": token}).encode("ascii"), method="POST")
    r.add_header("Content-Type","application/x-www-form-urlencoded")
    r.add_header("x-auth-formtoken", token)
    f = urllib.request.urlopen(r)
    d = json.loads(f.read().decode("ascii"))
    if d.get("success", False):
        return d["session"]
    return None

def request(session, path, keepalive=False):
    r = urllib.request.Request(urllib.parse.urljoin("https://www.irccloud.com/", path))
    r.add_header("User-Agent", "IRCClive")
    r.add_header("Cookie", "session=" + session)
    if keepalive:
        r.add_header("Connection", "keep-alive")
    return urllib.request.urlopen(r)

def stream(session):
    f = request(session, "/chat/stream", True)
    try:
        while True:
            d = f.readline()
            if d == b"":
                print("disconnected.")
                print("reconnecting...")
                run()
                break
            else:
                d = json.loads(d.decode("utf-8"))
                if d["type"] == "oob_include":
                    if oob_include(session, d["url"]):
                        print("connected successfully.")
                    else:
                        print("connection failed.")
                        print("reconnecting...")
                        run()
                        break
    except KeyboardInterrupt:
        print("terminating...")
    except:
        print()
        print(sys.exc_info()[0])
        print()
        print("reconnecting...")
        run()

def oob_include(session, url):
    f = request(session, url)
    return True if f.read() else False

def run():
    stream(login(email, password, auth_formtoken()))

if __name__ == "__main__":
    email, password = None, None
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if not email:
        email = input("email: ")
    if not password:
        password = input("password: ")
    print("connecting...")
    run()
