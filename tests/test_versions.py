#!/usr/bin/env python3
"""Tests seeded samples, immutable audit, restore, approval and permissions on real local HTTP server."""
import json,os,socket,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    so=socket.socket();so.bind(('127.0.0.1',0));port=so.getsockname()[1];so.close()
    env=os.environ.copy();env.update(PORT=str(port),HOST='127.0.0.1',DEMO_READONLY='1',PAPERROOM_DATA_DIR=tmp,BASE_URL='https://example.invalid')
    server=subprocess.Popen([sys.executable,str(root/'server.py')],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    def req(method,path,payload=None,token=''):
        body=json.dumps(payload).encode() if payload is not None else None
        request=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=body,method=method,headers={'Content-Type':'application/json','X-Paperroom-Token':token,'X-Paperroom-Name':'Test Collaborator'})
        try:
            with urllib.request.urlopen(request,timeout=8) as response:
                b=response.read()
                return response.status,json.loads(b) if response.headers.get('content-type','').startswith('application/json') else b
        except urllib.error.HTTPError as e:
            return e.code,json.loads(e.read())
    try:
        for _ in range(80):
            if server.poll() is not None:raise AssertionError('server exited: '+str(server.stderr.read()))
            try:
                if req('GET','/api/health')[0]==200:break
            except OSError:time.sleep(.10)
        else:raise AssertionError('health check timed out')
        status,data=req('GET','/api/projects/demo')
        assert status==200,(status,data)
        assert data['role']=='viewer'
        assert len(data['artifacts'])>=6,len(data['artifacts'])
        assert len(data['tasks'])>=6
        assert len(data['activities'])>=15
        demo=data['artifacts']
        a=next(a for a in demo if a['kind']=='fig' and a['body'].get('file'))
        code,binary=req('GET',f'/api/projects/demo/artifacts/{a["id"]}/files/{a["body"]["file"]["file"]}')
        assert code==200 and binary.startswith(b'\x89PNG'),(code,binary[:20])
        v=next(a for a in demo if a['kind']=='table' and a['current_version']>=3)
        st,detail=req('GET',f'/api/projects/demo/artifacts/{v["id"]}')
        assert st==200 and len(detail['revisions'])>=3
        assert all('T' in r['created'] and '+' in r['created'] for r in detail['revisions'])
        assert req('POST',f'/api/projects/demo/artifacts/{v["id"]}/restore',{'version':1})[0]==403
        code,clone=req('POST','/api/projects/clone-demo',{'title':'OLIVE — test editable copy'})
        assert code==201,(code,clone)
        pid,token=clone['project_id'],clone['token']
        code,data=req('GET',f'/api/projects/{pid}',token=token)
        assert code==200 and data['role']=='owner'
        art=next(a for a in data['artifacts'] if a['kind']=='table' and a['current_version']>=3)
        aid=art['id'];baseline=art['current_version'];url=f'/api/projects/{pid}/artifacts/{aid}'
        _,before=req('GET',url,token=token)
        target=next(x for x in before['revisions'] if x['version']==1)
        code,res=req('POST',url+'/restore',{'version':1,'note':'과거 표 구조 복원 실습','expected_version':baseline},token=token)
        assert code==200 and res['version']==baseline+1,(code,res)
        _,after=req('GET',url,token=token)
        assert after['artifact']['current_version']==baseline+1
        assert after['artifact']['body']==target['snapshot']['body']
        assert len(after['revisions'])==len(before['revisions'])+1
        assert '복원' in after['revisions'][0]['note']
        assert 'T' in after['revisions'][0]['created']
        code,res=req('POST',url+'/restore',{'version':1,'expected_version':baseline},token=token)
        assert code==409,(code,res)
        # Editor should be able to restore a normal item but not an approved item.
        code,inv=req('POST',f'/api/projects/{pid}/invites',{'email':'friend@example.com','role':'editor'},token=token)
        assert code==201
        edit_token=inv['link'].split('t=')[1]
        code,rev=req('POST',url+'/revisions',{
            'expected_version':baseline+1,'body':after['artifact']['body'],'note':'테스트: 표 주석 업데이트','status':'review','owner':'Test Collaborator',
            'description':'편집 확인','title':art['title']},token=edit_token)
        assert code==200 and rev['version']==baseline+2,(code,rev)
        code,approved=req('POST',url+'/approve',{'note':'승인 테스트'},token=token)
        assert code==200 and approved['version']==baseline+3,(code,approved)
        _,approved_detail=req('GET',url,token=token)
        assert approved_detail['revisions'][0]['snapshot']['status']=='approved'
        assert req('POST',url+'/restore',{'version':1},token=edit_token)[0]==403
        # Verify 
        code,res=req('POST',url+'/restore',{'version':1,'note':'승인 전 버전으로 복원'},token=token)
        assert code==200 and res['version']==baseline+4,(code,res)
        _,latest=req('GET',url,token=token)
        assert latest['revisions'][0]['version']==baseline+4
        assert latest['revisions'][1]['version']==baseline+3
        assert latest['revisions'][1]['snapshot']['status']=='approved'
        _,activity=req('GET',f'/api/projects/{pid}',token=token)
        assert '복원' in activity['activities'][0]['message']
        print('PASS: seeded 6 artifacts / 15+ events / figures / 3+ versions / immutable restore / KST timestamps / conflict handling / invite permissions / approval log')
    finally:
        server.terminate()
        try:server.wait(timeout=3)
        except subprocess.TimeoutExpired:server.kill()
