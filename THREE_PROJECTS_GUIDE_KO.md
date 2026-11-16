# PAPER ROOM v3.4 — 세 논문 기반 공개 예시

## 프로젝트 구성

1. 진행 중: `Cross-Environment LiDAR–Camera Misalignment Detection via Object-Level VLM Assessment` (구 OLIVE 프로젝트) — 기존 Fig. 1–6, Table I–III 유지
2. **완료**: `특징점이 부족한 실내환경에서의 Visual Localization 에 대한 연구` — 논문 Fig. 1–4, Table 1
3. **완료**: `MARSCalib: Multi-robot, Automatic, Robust, Spherical Target-based Extrinsic Calibration in Field and Extraterrestrial Environments` — 논문 Fig. 1–9, Table I–III

## 실제 원문과 데모 기록의 구분

- 그림과 표 결과는 첨부 PDF 원문에서 추출하거나 실제 수치를 옮겼습니다.
- Visual Localization의 Table 1은 오류율 0.286/0.143/0.071, 소요시간 1.71/2.92/17.39ms를 사용합니다.
- MARSCalib Table I의 센서 오염 2개 행, Table II의 제안방법 Ours 9개 조합, Table III의 A/B/C 및 평균치를 사용합니다. **Table I·II는 원문 표에서 발췌한 항목**임을 각 표 설명에 명시했습니다.
- 가상 연구자, 작업 시작일, 수정 단계/메모, 피드백, 완료 체크, 승인 날짜는 모두 **수업 시연용으로 재구성한 가상 이력**입니다. 실제 공동저자의 행동이나 사실로 제시하지 마세요.
- 두 완료 프로젝트의 그림과 표는 모두 `승인 완료`, 할 일은 모두 완료입니다.
- 각 결과물에 v1 초안→v2 검토→v3 승인 기록이 있으며, 메모와 한국시간(KST) 타임스탬프가 포함됩니다.
- 무료 Render 프로젝트는 공개 열람만 허용하지만, **편집 체험 시작**을 선택하면 각각의 프로젝트를 비공개 사본으로 복제해 수정/복원할 수 있습니다.

## 공개 주소 경로

- 메인(기존 논문 이름 변경): `https://<Render-URL>/?w=demo`
- 완료된 Visual Localization: `https://<Render-URL>/?w=demo-visual`
- 완료된 MARSCalib: `https://<Render-URL>/?w=demo-mars`
- 왼쪽 프로젝트 이름을 클릭하거나 첫 페이지의 프로젝트 카드에서 서로 전환할 수 있습니다.

## GitHub → Render 반영

1. 이 ZIP을 압축 해제합니다.
2. `server.py`, `static/`, `seed_assets/`, `Dockerfile`, `render.yaml`, `requirements.txt`를 **기존 GitHub 저장소 최상위**에 업로드합니다.
3. 덮어쓰기가 필요한 파일(예: `server.py`, `static/app.js`)은 GitHub 웹 업로드에서 기존 파일을 대체하거나 git으로 커밋해야 합니다. 같은 파일이 중복 디렉터리에 있지 않도록 확인하세요.
4. Render → `Manual Deploy` → `Deploy latest commit` (자동 배포라면 불필요).
5. 배포 후 `https://<Render-URL>/?w=demo-visual`, `.../?w=demo-mars`에서 확인합니다.

## 무료 배포 주의

- Render Free의 로컬 SQLite 데이터는 영구 보관되지 않습니다. 공개 데모 3개는 서버 재시작 시 다시 생성됩니다.
- 사용자가 편집 체험으로 만든 사본은 서버 재시작 시 사라질 수 있습니다. 제출용 완성 프로젝트는 항상 원본 seeding으로 다시 표시됩니다.
- `DEMO_READONLY=1`을 유지하세요.

## 테스트

`python3 tests/test_three_papers.py`
