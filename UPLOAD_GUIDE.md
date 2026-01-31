# jaso-jamo pip 업로드 가이드

## 사전 준비

### 1. PyPI 계정 생성
- [PyPI](https://pypi.org/account/register/)에서 계정 생성
- [TestPyPI](https://test.pypi.org/account/register/)에서 테스트 계정 생성 (선택사항)

### 2. API 토큰 생성
1. PyPI 로그인 후 Account Settings → API tokens
2. "Add API token" 클릭
3. Token name: `jaso-jamo` (또는 원하는 이름)
4. Scope: "Entire account" 또는 "Project: jaso-jamo"
5. 생성된 토큰 복사 (다시 볼 수 없음)

### 3. 빌드 도구 설치

```bash
pip install --upgrade build twine
```

## 패키지 빌드

### 1. 버전 확인
`pyproject.toml`에서 버전 번호 확인 및 업데이트:

```toml
[project]
name = "jaso-jamo"
version = "1.0.0"  # 새 릴리스마다 증가
```

### 2. 빌드 실행

```bash
# 프로젝트 루트에서 실행
python -m build
```

빌드가 성공하면 `dist/` 폴더에 다음 파일이 생성됩니다:
- `jaso-jamo-1.0.0.tar.gz` (소스 배포판)
- `jaso_jamo-1.0.0-py3-none-any.whl` (휠 배포판)

## TestPyPI에 업로드 (테스트)

### 1. TestPyPI 업로드

```bash
python -m twine upload --repository testpypi dist/*
```

Username: `__token__`
Password: (TestPyPI API 토큰 입력)

### 2. TestPyPI에서 설치 테스트

```bash
pip install --index-url https://test.pypi.org/simple/ jaso-jamo
```

### 3. 동작 확인

```python
from jaso_jamo import tokenize, detokenize

text = "한글"
tokens = tokenize(text)
print(tokens)  # ['ㅎ', 'ㅏ', 'ㄴ', 'ㄱ', 'ㅡ', 'ㄹ']
print(detokenize(tokens))  # '한글'
```

## PyPI에 업로드 (배포)

### 1. 최종 확인
- [ ] 모든 테스트 통과
- [ ] README.md 확인
- [ ] 버전 번호 확인
- [ ] CHANGELOG 업데이트 (있는 경우)

### 2. PyPI 업로드

```bash
python -m twine upload dist/*
```

Username: `__token__`
Password: (PyPI API 토큰 입력)

### 3. 설치 확인

```bash
pip install jaso-jamo
```

## 배포 자동화 (.pypirc)

`~/.pypirc` 파일을 생성하여 자동화할 수 있습니다:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgE...  # PyPI API 토큰

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE...  # TestPyPI API 토큰
```

**보안 주의**: `.pypirc` 파일은 절대 git에 커밋하지 마세요!

## GitHub Actions 자동 배포

`.github/workflows/publish.yml` 파일을 사용하여 태그 푸시 시 자동 배포:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Secrets에 `PYPI_API_TOKEN` 등록 필요.

## 버전 관리

### Semantic Versioning (SemVer)
- `MAJOR.MINOR.PATCH` 형식 사용
- `1.0.0` → 첫 안정 릴리스
- `1.0.1` → 버그 수정
- `1.1.0` → 새 기능 추가 (하위 호환)
- `2.0.0` → 주요 변경 (하위 호환 깨짐)

### 버전 업데이트 순서
1. `pyproject.toml`의 `version` 업데이트
2. `jaso_jamo/__init__.py`의 `__version__` 업데이트
3. CHANGELOG 업데이트 (있는 경우)
4. 커밋 및 태그: `git tag v1.0.1`

## 주의사항

1. **버전 고유성**: 같은 버전 번호로 재업로드 불가능
2. **테스트 필수**: TestPyPI에서 먼저 테스트
3. **파일 정리**: 이전 빌드 파일 삭제 후 재빌드
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```
4. **보안**: API 토큰을 코드에 포함하지 마세요
5. **의존성**: `pyproject.toml`의 dependencies 확인

## 트러블슈팅

### 빌드 실패
```bash
# 캐시 정리
rm -rf build/ dist/ *.egg-info
pip install --upgrade setuptools wheel build
python -m build
```

### 업로드 실패: 403 Forbidden
- API 토큰 확인
- 패키지명 중복 확인 (PyPI에서 검색)

### 업로드 실패: 400 Bad Request
- 버전 번호 중복 (이미 업로드된 버전)
- `pyproject.toml`의 버전 번호 증가

## 참고 자료

- [PyPI 공식 문서](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 문서](https://twine.readthedocs.io/)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)
