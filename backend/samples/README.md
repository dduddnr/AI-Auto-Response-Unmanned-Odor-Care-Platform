# samples

공공 API의 **실제 응답 원본**을 저장한다. 커넥터 개발·테스트의 기준 자료.

## 커밋 전 필수 확인

공공데이터포털 API(에어코리아 등)는 인증키를 URL 쿼리(`serviceKey=...`)로 보낸다.
응답 본문·에러 메시지·로그에 요청 URL이 함께 저장되는 경우가 많으므로, 커밋 전에 반드시 확인한다.

```bash
grep -rinE "service_?key" backend/samples/
```

- 결과가 나오면 값을 `REDACTED`로 바꾼 뒤 커밋한다.
- 요청 URL을 남겨야 하면 `serviceKey=REDACTED`로 적는다.
- 이미 푸시된 키는 지우는 것만으로는 부족하다 (커밋 이력에 남음). 키를 폐기하고 재발급한다.

gitleaks로도 검사할 수 있다 (`.gitleaks.toml`에 `serviceKey` 전용 규칙 포함, 레포 루트에서 실행). `git` 모드는 커밋된 이력만 보므로, 커밋 전에는 `--staged`를 붙인다.

```bash
# 커밋 전: git add 한 파일 검사
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo --staged --config /repo/.gitleaks.toml --redact

# 푸시 전: 커밋 이력 전체 검사
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo --config /repo/.gitleaks.toml --redact
```

## 파일 이름 규칙

`{출처}_{API명}_{조회일시}.json` 예) `airkorea_getMsrstnAcctoRltmMesureDnsty_20260929T1400.json`
