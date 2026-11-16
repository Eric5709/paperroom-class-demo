#!/usr/bin/env python3
"""Local end-to-end test; stdlib only."""
import json, os, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error
from pathlib import Path

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    sock=socket.socket();sock.bind(("127.0.0.1",0));port=sock.getsockname()[1];sock.close()
    env=os.environ.copy()
    env.update(HOST="127.0.0.1",PORT=str(port),PAPERROOM_DATA_DIR=temp,
               DEMO_READONLY="1",BASE_URL="https://paperroom.example.test")
    proc=subprocess.Popen([sys.executable,str(root/"server.py")],env=env,cwd=root,
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def req(method,path,body=None,token=None):
        data=json.dumps(body).encode() if body is not None else None
        headers={"Content-Type":"application/json"}
        if token: headers["X-Paperroom-Token"]=token
        q=urllib.request.Request(f"http://127.0.0.1:{port}{path}",data=data,headers=headers,method=method)
        try:
            with urllib.request.urlopen(q,timeout=3) as r:
                return r.status,json.load(r)
        except urllib.error.HTTPError as e:
            return e.code,json.load(e)
    try:
        for _ in range(60):
            try:
                st,_=req("GET","/api/health")
                if st==200: break
            except OSError:time.sleep(.1)
        else:raise AssertionError("Server never started")

        st,project=req("POST","/api/projects",{"title":"Research Test"})
        assert st==201, (st,project)
        pid,owner=project["project_id"],project["token"]
        st,_=req("GET",f"/api/projects/{pid}")
        assert st==403,st
        st,invite=req("POST",f"/api/projects/{pid}/invites",
                        {"email":"collab@example.edu","role":"viewer"},owner)
        assert st==201 and invite["link"].startswith("https://paperroom.example.test/"),invite
        assert invite["delivery"]=="mail_app",invite
        token=invite["link"].split("t=")[1]
        st,_=req("POST",f"/api/projects/{pid}/artifacts",
                  {"title":"Fig X","kind":"fig"},token)
        assert st==403,st
        st,fig=req("POST",f"/api/projects/{pid}/artifacts",
                   {"title":"Fig 1","kind":"fig"},owner)
        assert st==201, (st,fig)
        st,view=req("GET",f"/api/projects/{pid}",token=token)
        assert st==200 and len(view["artifacts"])==1,(st,view)
        st,demo=req("GET","/api/projects/demo")
        assert st==200 and demo["role"]=="viewer",(st,demo)
        st,_=req("POST","/api/projects/demo/artifacts",
                   {"title":"NO","kind":"fig"})
        assert st==403,st
        st,owner_view=req("GET",f"/api/projects/{pid}",token=owner)
        assert st==200 and len(owner_view["invites"])==1
        st,_=req("DELETE",f"/api/projects/{pid}/invites/{owner_view['invites'][0]['id']}",token=owner)
        assert st==200,st
        st,_=req("GET",f"/api/projects/{pid}",token=token)
        assert st==403,st
        assert Path(temp,"paperroom.sqlite3").exists()
        print("PASS: health, create, private access, invite link, viewer permissions, persistence, revoke, readonly demo")
    finally:
        proc.terminate()
        try:proc.wait(timeout=2)
        except subprocess.TimeoutExpired:proc.kill()
