# jaso-jamo 빌드 및 테스트 가이드

## 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/c0z0c/jaso-jamo.git
cd jaso-jamo
```

### 2. 가상 환경 설정 (권장)

```bash
# Python venv 사용
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 또는 conda 사용
conda create -n jaso-jamo python=3.11
conda activate jaso-jamo
```

### 3. 개발 모드로 설치

```bash
# 기본 패키지 설치
pip install -e .

# 개발 의존성 포함 설치
pip install -e ".[dev]"
```

개발 의존성:
- pytest (테스트)
- pytest-cov (커버리지)
- black (포맷터)
- isort (import 정리)

## 로컬 빌드

### 1. 빌드 도구 설치

```bash
pip install --upgrade build
```

### 2. 패키지 빌드

```bash
python -m build
```

빌드 결과물 (`dist/` 폴더):
- `jaso-jamo-1.0.2.tar.gz` - 소스 배포판
- `jaso_jamo-1.0.2-py3-none-any.whl` - 휠 배포판

### 3. 빌드 정리

```bash
# 빌드 아티팩트 제거
rm -rf dist/ build/ *.egg-info

# Windows
Remove-Item -Recurse -Force dist, build, *.egg-info
```

## 테스트

### 단위 테스트

```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 테스트 파일 실행
pytest tests/test_basic.py -v

# 커버리지 리포트 포함
pytest tests/ --cov=jaso_jamo --cov-report=html
```

### 벤치마크 테스트

```bash
# 벤치마크 실행
python benchmarks/run_benchmark.py

# 결과 확인
cat report/[timestamp]_benchmark_report.md
```

### 개별 테스트 실행

```bash
# 기본 기능 테스트
python tests/test_basic.py

# 엣지 케이스 테스트
python tests/test_edge_cases.py

# 종성 테스트
python tests/test_jongseong.py

# 슬랭 경계 테스트
python tests/test_slang_boundary.py
```

## 코드 품질

### 포맷팅

```bash
# Black으로 자동 포맷팅
black jaso_jamo/ tests/

# 포맷 확인만
black --check jaso_jamo/ tests/
```

### Import 정리

```bash
# isort로 import 정리
isort jaso_jamo/ tests/

# 확인만
isort --check-only jaso_jamo/ tests/
```

### 린팅

```bash
# ruff로 린팅
ruff check jaso_jamo/ tests/

# 자동 수정 가능한 것 수정
ruff check --fix jaso_jamo/ tests/
```

## 로컬 설치 테스트

### 1. 빌드된 패키지 설치

```bash
# wheel 파일로 설치
pip install dist/jaso_jamo-1.0.2-py3-none-any.whl

# 또는 tar.gz로 설치
pip install dist/jaso-jamo-1.0.2.tar.gz
```

### 2. 동작 확인

```python
python -c "from jaso_jamo import tokenize, detokenize; print(detokenize(tokenize('한글')))"
# 출력: 한글
```

### 3. 제거

```bash
pip uninstall jaso-jamo
```

## CI/CD 확인

### GitHub Actions 로컬 테스트 (act)

```bash
# act 설치 (https://github.com/nektos/act)
# macOS
brew install act

# Ubuntu
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# CI 워크플로우 실행
act -j test

# Publish 워크플로우 실행 (dry-run)
act workflow_dispatch -j build
```

## 버전 릴리스 체크리스트

- [ ] 모든 테스트 통과 (`pytest tests/ -v`)
- [ ] 벤치마크 성능 확인 (`python benchmarks/run_benchmark.py`)
- [ ] 코드 포맷팅 확인 (`black --check .`)
- [ ] Import 정리 확인 (`isort --check-only .`)
- [ ] `pyproject.toml` 버전 업데이트
- [ ] `jaso_jamo/__init__.py` `__version__` 업데이트
- [ ] CHANGELOG.md 작성 (있는 경우)
- [ ] README.md 업데이트 확인
- [ ] 로컬 빌드 테스트 (`python -m build`)
- [ ] TestPyPI 업로드 테스트
- [ ] Git 태그 생성 (`git tag v1.0.0`)
- [ ] GitHub에 푸시 (`git push origin v1.0.0`)

## 트러블슈팅

### 빌드 실패: ModuleNotFoundError

```bash
pip install --upgrade setuptools wheel build
```

### 테스트 실패: ImportError

```bash
# 개발 모드로 재설치
pip uninstall jaso-jamo
pip install -e .
```

### 포맷팅 충돌

```bash
# 캐시 정리
black --clear
isort --rm-cache
```

### pytest 캐시 문제

```bash
# pytest 캐시 정리
rm -rf .pytest_cache
pytest --cache-clear
```

## 참고 자료

- [Python Packaging User Guide](https://packaging.python.org/)
- [pytest 문서](https://docs.pytest.org/)
- [Black 문서](https://black.readthedocs.io/)
- [isort 문서](https://pycqa.github.io/isort/)
