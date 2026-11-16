#!/usr/bin/env python3
"""Validate PDF-grounded seed values, immutable histories and Render-style server migration."""
import os,json,sys,socket,tempfile,subprocess,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'paperroom_fix_tmp'/'server.py'

def random_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));return s.getsockname()[1]

def start(source,datadir):
    port=random_port();env=os.environ.copy();env.update(HOST='127.0.0.1',PORT=str(port),PAPERROOM_DATA_DIR=str(datadir),DEMO_READONLY='1')
    proc=subprocess.Popen([sys.executable,str(source)],cwd=source.parent,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    def req(method,path,payload=None,token=''):
        data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None
        req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=data,method=method,
                 headers={'Content-Type':'application/json','X-Paperroom-Name':'%EA%B0%80%EC%83%81%20%EC%97%B0%EA%B5%AC%EC%9E%90','X-Paperroom-Token':token})
        try:
            with urllib.request.urlopen(req,timeout=7) as response:
                b=response.read()
                return response.status,json.loads(b) if response.headers.get('content-type','').startswith('application/json') else b
        except urllib.error.HTTPError as e:
            return e.code,json.loads(e.read())
    for _ in range(100):
        if proc.poll() is not None:raise RuntimeError('Server exited: '+proc.stderr.read().decode()[:2000])
        try:
            if req('GET','/api/health')[0]==200:return proc,req
        except OSError:time.sleep(.10)
    raise RuntimeError('server failed startup')

def stop(proc):
    proc.terminate()
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:proc.kill()

with tempfile.TemporaryDirectory() as tmp:
    p,api=start(ROOT/'server.py',Path(tmp))
    try:
        status,d=api('GET','/api/projects/demo')
        assert status==200,(status,d)
        assert d['project']['is_demo']==1 and d['role']=='viewer'
        assert d['project']['title']=='Cross-Environment LiDAR–Camera Misalignment Detection via Object-Level VLM Assessment'
        assert len(d['artifacts'])==9,len(d['artifacts'])
        assert sum(a['kind']=='fig' for a in d['artifacts'])==6
        assert sum(a['kind']=='table' for a in d['artifacts'])==3
        assert len(d['tasks'])==10 and sum(t['done'] for t in d['tasks'])==3
        assert len(d['activities'])>=25
        for artifact in d['artifacts']:
            assert artifact['owner'].startswith('가상 연구자')
            assert artifact['current_version']>=2
            status,item=api('GET',f'/api/projects/demo/artifacts/{artifact["id"]}')
            assert status==200 and len(item['revisions'])==artifact['current_version']
            assert all('+' in r['created'] for r in item['revisions'])
            assert all(r['note'] for r in item['revisions'])
            if artifact['kind']=='fig':
                key=artifact['body']['file']['file']
                code,b=api('GET',f'/api/projects/demo/artifacts/{artifact["id"]}/files/{key}')
                assert code==200 and b.startswith(b'\x89PNG\r\n\x1a\n')
        table1=next(a for a in d['artifacts'] if a['title'].startswith('Table I '))
        assert table1['body']['rows']==[['Pass','97.51','59.97'],['Fail','81.12','73.22'],['Unknown','85.50','96.02']]
        table2=next(a for a in d['artifacts'] if a['title'].startswith('Table II '))
        assert [(r[0],r[3],r[4]) for r in table2['body']['rows']]==[
              ('KITTI','160','240'),('WOD','30','45'),('DiTer++','95','143'),('Pohang','30','45')]
        table3=next(a for a in d['artifacts'] if a['title'].startswith('Table III '))
        assert len(table3['body']['rows'])==16
        assert [r[2] for r in table3['body']['rows'] if r[1]=='Ours']==['89.50','76.00','74.79','82.67']
        code,details=api('GET',f'/api/projects/demo/artifacts/{table3["id"]}')
        assert [len(r['snapshot']['body']['rows']) for r in reversed(details['revisions'])]==[4,8,12,16]
        clone_status,clone=api('POST','/api/projects/clone-demo',{'title':'OLIVE 편집 데모 복제'})
        assert clone_status==201
        cid=clone['project_id'];token=clone['token']
        code,copied=api('GET',f'/api/projects/{cid}',token=token)
        assert code==200 and len(copied['artifacts'])==9
        clonefig=next(a for a in copied['artifacts'] if a['kind']=='fig')
        code,png=api('GET',f'/api/projects/{cid}/artifacts/{clonefig["id"]}/files/{clonefig["body"]["file"]["file"]}',token=token)
        assert code==200 and png.startswith(b'\x89PNG')
        ctable=next(a for a in copied['artifacts'] if a['title'].startswith('Table III '))
        code,before=api('GET',f'/api/projects/{cid}/artifacts/{ctable["id"]}',token=token)
        code,res=api('POST',f'/api/projects/{cid}/artifacts/{ctable["id"]}/restore',{
                      'version':1,'note':'시연용 1차 표로 복원','expected_version':4},token=token)
        assert code==200 and res['version']==5,(code,res)
        code,after=api('GET',f'/api/projects/{cid}/artifacts/{ctable["id"]}',token=token)
        assert len(after['artifact']['body']['rows'])==4 and len(after['revisions'])==5
        assert '복원' in after['revisions'][0]['note']
        print('PASS: 6 paper figures / 3 exact source tables / 10 tasks / revision history / source image access / restore as v5')
    finally:stop(p)

# Test migration from previously deployed demo without destroying private projects or clones.
if OLD.exists():
    with tempfile.TemporaryDirectory() as tmp:
        o,oldapi=start(OLD,Path(tmp))
        try:
            s,user=oldapi('POST','/api/projects',{'title':'이전 사용자 개인 프로젝트'})
            assert s==201
            private_id,private_token=user['project_id'],user['token']
        finally:stop(o)
        n,newapi=start(ROOT/'server.py',Path(tmp))
        try:
            st,d=newapi('GET','/api/projects/demo')
            assert st==200 and len(d['artifacts'])==9
            st,own=newapi('GET',f'/api/projects/{private_id}',token=private_token)
            assert st==200 and own['project']['title']=='이전 사용자 개인 프로젝트'
            print('PASS: old seeded demo migration upgrades only demo, retains existing private project')
        finally:stop(n)
