#!/usr/bin/env python3
"""Check all three paper demos, exact metrics, version history, completed status and restore."""
import json,os,socket,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
    env=os.environ.copy();env.update(HOST='127.0.0.1',PORT=str(port),PAPERROOM_DATA_DIR=tmp,DEMO_READONLY='1')
    process=subprocess.Popen([sys.executable,str(root/'server.py')],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    def req(method,path,payload=None,token=''):
        data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None
        q=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=data,method=method,headers={'Content-Type':'application/json','X-Paperroom-Token':token,'X-Paperroom-Name':'%EA%B9%80%EC%97%B0%EA%B5%AC'})
        try:
            with urllib.request.urlopen(q,timeout=10) as r:
                body=r.read();typ=r.headers.get('content-type','')
                return r.status,json.loads(body) if typ.startswith('application/json') else body
        except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
    try:
        for _ in range(100):
            if process.poll() is not None:raise RuntimeError(process.stderr.read().decode()[:2500])
            try:
                if req('GET','/api/health')[0]==200:break
            except OSError:time.sleep(.1)
        else:raise AssertionError('server not ready')
        st,pubs=req('GET','/api/public-projects');assert st==200 and len(pubs)==3, (st,pubs)
        assert [x['id'] for x in pubs]==['demo','demo-visual','demo-mars']
        assert pubs[0]['title']=='Cross-Environment LiDAR–Camera Misalignment Detection via Object-Level VLM Assessment'
        expected_counts={'demo':(6,3),'demo-visual':(4,1),'demo-mars':(9,3)}
        for pid,(fcount,tcount) in expected_counts.items():
            status,project=req('GET',f'/api/projects/{pid}')
            assert status==200 and project['role']=='viewer',(pid,status)
            a=project['artifacts']
            assert len(a)==fcount+tcount,(pid,len(a))
            assert sum(x['kind']=='fig' for x in a)==fcount
            assert sum(x['kind']=='table' for x in a)==tcount
            assert len(project['activities'])>10
            for x in a:
                status,detail=req('GET',f'/api/projects/{pid}/artifacts/{x["id"]}')
                assert status==200
                assert len(detail['revisions'])==x['current_version']
                assert all('가상' in rev['note'] if pid!='demo' else bool(rev['note']) for rev in detail['revisions'])
                assert all('+09:00' in rev['created'] for rev in detail['revisions'])
                if pid!='demo':
                    assert x['status']=='approved' and x['current_version']==3
                    assert [r['snapshot']['status'] for r in reversed(detail['revisions'])]==['draft','review','approved']
                    assert detail['comments']
                if x['kind']=='fig':
                    f=x['body']['file']['file'];code,binary=req('GET',f'/api/projects/{pid}/artifacts/{x["id"]}/files/{f}')
                    assert code==200 and binary.startswith(b'\x89PNG\r\n\x1a\n'),(pid,x['title'])
            if pid!='demo':
                assert all(x['done']==1 for x in project['tasks']) and len(project['tasks'])>=6
                assert all('가상' in x['owner'] for x in a)
                assert all('가상' in x['message'] or '완료' in x['message'] for x in project['activities'])
                code,_=req('POST',f'/api/projects/{pid}/artifacts',{'title':'do not allow','kind':'fig'})
                assert code==403
            if pid=='demo-visual':
                t=next(x for x in a if x['kind']=='table');assert t['body']['rows']==[['5','0.286','1.71'],['20','0.143','2.92'],['No Retrieval','0.071','17.39']]
            if pid=='demo-mars':
                table1=next(x for x in a if x['title'].startswith('Table I '));assert table1['body']['rows']==[['Blur','1/6','4/6','6/6'],['Mud','0/6','3/6','6/6']]
                table2=next(x for x in a if x['title'].startswith('Table II '));assert len(table2['body']['rows'])==9
                table3=next(x for x in a if x['title'].startswith('Table III '));assert table3['body']['rows'][-1]==['평균','전체','0.0308','1.4620','0.1143','2.0405']
        for pid in ['demo-visual','demo-mars']:
            status,clone=req('POST','/api/projects/clone-demo',{'title':'검증용 수정 가능 사본','source_id':pid})
            assert status==201,(status,clone)
            cid,token=clone['project_id'],clone['token']
            st,d=req('GET',f'/api/projects/{cid}',token=token);assert st==200 and d['role']=='owner'
            assert len(d['artifacts'])==sum(expected_counts[pid])
            table=next(x for x in d['artifacts'] if x['kind']=='table')
            aid=table['id'];body=table['body']
            st,r=req('POST',f'/api/projects/{cid}/artifacts/{aid}/restore',{'version':1,'note':'과거 표로 회귀 테스트','expected_version':3},token=token)
            assert st==200 and r['version']==4 and r['restored_from']==1,(st,r)
            st,v=req('GET',f'/api/projects/{cid}/artifacts/{aid}',token=token)
            assert st==200 and len(v['revisions'])==4
            assert v['artifact']['body']==v['revisions'][-1]['snapshot']['body']
        st,bad=req('POST','/api/projects/clone-demo',{'source_id':'not-public','title':'Oops'})
        assert st==400
        print('PASS: three demo projects, 19 figures, 7 tables, all completed states, actual table metrics, public switch list, images, version history, copy+rollback')
    finally:
        process.terminate()
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill()
