# PAPER ROOM v3 — 학교 과제 제출 가이드 (무료)

## 결과물
- `https://<your-service>.onrender.com/` 형태의 **교수님이 누구나 열 수 있는 공개 URL**
- 계정 없이 접근 가능한 `OLIVE — Paper Writing Workspace` 읽기 전용 데모 (시연용 가상 팀 데이터)
- Fig. 1/2/3, Table 1/2/3: 6개 예시 작업, 단계별 v1~v3, 담당자, 상태, To-do, 의견, 활동 로그
- 모든 버전에 ISO 8601 시간(저장은 UTC 또는 offset-aware), 화면에는 **한국 시간 KST 날짜·시·분·초** 표시
- 버전 변경 메모 및 이전 버전 미리보기/비교
- 이전 버전 복원: 기존 버전을 덮어쓰지 않고 **새 버전**으로 기록. 복원 사유도 저장
- 공개 데모는 읽기 전용; `편집 체험 시작`으로 사본을 생성해 저장/복원/초대 테스트 가능

## 가장 간단한 무료 공개 URL 배포
1. GitHub에서 **빈 저장소**를 만듭니다. 예: `paperroom-class-project`.
2. ZIP의 `PaperRoom_v3_ClassDemo` 폴더 **안에 있는 파일들** (`server.py`, `Dockerfile`, `static/`, `seed_assets/`, `render.yaml` 등)을 GitHub 저장소 최상위에 업로드합니다. ZIP 자체만 올리면 안 됩니다.
3. Render > **New > Blueprint** > GitHub 저장소 연결 > `render.yaml` 인식.
4. 서비스 비용이 **Free ($0)**인지 확인해 배포합니다. 영구 디스크는 추가하지 않습니다.
5. Render에 표시되는 `https://...onrender.com` 주소를 복사해 제출합니다. URL 마지막은 `/`여도 되고 `/?w=demo`를 붙여도 됩니다.
6. 데모 URL을 **시크릿 창**에서 열어 미리 확인합니다. 최초 접속은 서버의 휴면 해제로 최대 약 1분 지연될 수 있습니다.

### 필수 주의: 이 방법은 URL+시연용
Render Free는 15분 동안 유휴 상태가 되면 스핀다운하며, 로컬 SQLite DB와 수정 내용이 사라집니다. 재기동 시 **데모 기본 자료는 다시 자동 생성**되지만, `편집 체험`으로 생성한 개별 사본과 편집 로그는 사라질 수 있습니다. **과제 제출 화면의 기본 데모 자체는 유지**됩니다.

## 실제 협업 로그를 오래 보존하면서도 무료: Neon PostgreSQL (선택)
위 Render 무료 서버는 그대로 두고 **Neon 무료 PostgreSQL 데이터베이스**를 연동합니다.
1. https://neon.com/ 에서 무료 계정/프로젝트를 만들고 **Connection String** (`postgresql://...`)을 확인합니다.
2. Render 서비스 > **Environment** > **Add Environment Variable**: Key=`DATABASE_URL`, Value=Neon PostgreSQL 연결 문자열. 비밀번호이므로 절대 GitHub나 공용 채팅에 붙여넣지 마세요.
3. **Save, rebuild, and deploy** 또는 **Save and deploy**. 이제 프로젝트, 버전 메모, 댓글, 초대, 첨부 이미지가 Postgres DB에 저장됩니다.
4. 다시 공개 URL로 들어가 샘플 데이터 표시 및 편집 체험 기능을 점검합니다.

Neon 무료 요금제는 2026-10 기준 프로젝트당 1GB PostgreSQL 저장 공간과 월 100 CU-hours를 제공하며, 5분 유휴 시 compute만 일시 중지하고 저장 데이터는 유지합니다. 무료 한도를 초과하면 일시적으로 연결이 제한될 수 있습니다. 무료 약관과 잔여 사용량을 확인하세요.

**주의:** 이 코드의 PostgreSQL 백엔드는 별도 데이터베이스를 갖춘 실환경에서 end-to-end 테스트한 것은 아니고, 로컬 SQLite 기능 테스트를 통과했습니다. 실제 배포 후 꼭 Neon 연결과 데이터 유지 여부를 확인하세요. 과제 시연 안정성을 높이려면 교수님 접속 전 무료 Render 서비스/Neon DB에 직접 한 번 접속하는 것도 방법입니다.

## 시연 순서 (2분)
1. 개요: 진행률, 승인·검토·수정 중 결과물, 최근 로그를 확인.
2. Table 1 클릭 > **버전 기록** > 각 버전의 시각(KST)과 변경 메모 확인.
3. **현재와 비교**로 데이터 변화 확인.
4. 첫 화면의 **편집 체험 시작** > Table 1 > 버전 기록 > v1의 **이 버전 복원**.
5. 복원 메모 입력 후 **새 버전으로 복원** > v4와 복원 로그가 추가됐는지 확인.
6. 새 버전 저장, 댓글 등록, To-do 변경, 초대 링크 생성으로 기능 설명.

## 데이터와 보안
- 초기 기록은 **가상 작성자의 제출용 예시 데이터**입니다. 실제 공동연구자의 작업 이력을 나타내지 않습니다.
- 공개 데모는 읽기 전용이므로 방문자가 기본 예시를 지우거나 수정할 수 없습니다.
- 로그인 없는 초대는 **이메일 본인 인증이 아니라 링크 기반 권한 부여**입니다. SMTP가 없으면 사용자가 이메일 앱으로 초대 링크를 보냅니다.
- 무료 Render는 일반 SMTP 포트(25, 465, 587)로 메일 발송할 수 없습니다.
- 새 프로젝트의 소유자 링크는 비밀번호처럼 다뤄야 합니다. 실험 원본·미공개 연구 자료 등 민감한 파일은 사용하지 마세요.

## 설치/개발
```
python3 server.py
```
로컬 http://127.0.0.1:8765 (로컬은 DEMO_READONLY=0이 기본값). 공개 Render는 DEMO_READONLY=1.
```
python3 tests/test_smoke.py
python3 tests/test_versions.py
```
Python 3.10+ 필요. PostgreSQL 이용 시 `pip install -r requirements.txt` 필요.
