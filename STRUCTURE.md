# jaso-jamo 프로젝트 구조

```text
jaso-jamo/
│
├── jaso_jamo/                      # 핵심 라이브러리 패키지
│   ├── __init__.py                # 패키지 진입점
│   ├── core.py                    # 핵심 알고리즘 (JasoJamoTokenizer, JasoJamoDecoder)
│   ├── JasoJamoTokenizer.py       # 토크나이저 클래스
│   └── JasoJamoDecoder.py         # 디코더 클래스
│
├── pyproject.toml                  # 패키지 설정 (PEP 621)
├── MANIFEST.in                     # 배포 파일 제어
├── LICENSE                         # MIT 라이센스
├── README.md                       # 프로젝트 설명
├── STRUCTURE.md                    # 이 문서
├── BUILD_GUIDE.md                  # 빌드 가이드
├── UPLOAD_GUIDE.md                 # PyPI 업로드 가이드
├── DATA_LICENSE.md                 # 데이터 라이센스 (AI허브)
├── requirements.txt                # Python 의존성
├── environment.yml                 # Conda 환경
├── upload_jaso_jamo.py             # 업로드 스크립트
└── .gitignore                      # Git 제외 목록
```

## 배포 패키지 구조

pip으로 설치 시 포함되는 파일:

```text
jaso-jamo-1.0.2/
├── jaso_jamo/
│   ├── __init__.py
│   ├── core.py
│   ├── JasoJamoTokenizer.py
│   └── JasoJamoDecoder.py
├── README.md
├── LICENSE
└── [메타데이터]
```

**제외**: tests, benchmarks, article, report, .github

## 주요 파일 설명

### 핵심 라이브러리 (jaso_jamo/)

- **`__init__.py`**: 패키지 진입점, 주요 함수 export
- **`core.py`**: 핵심 알고리즘 통합
  - `tokenize()`, `detokenize()`: 편의 함수
- **`JasoJamoTokenizer.py`**: 자소 분리 클래스
- **`JasoJamoDecoder.py`**: 5단계 Fallback 자소 복원 클래스

### 테스트 (tests/)

- **`test_basic.py`**: 기본 기능 (5/5)
- **`test_edge_cases.py`**: 엣지 케이스 (40/40)
- **`test_jongseong.py`**: 종성 (17/17)
- **`test_slang_boundary.py`**: 슬랭 경계 (8/8)
- **전체 통과율: 100%**

### 벤치마크 (benchmarks/)

- **`baseline_libraries.py`**: 기존 방식 (unicodedata, Greedy, jamo)
- **`benchmark_runner.py`**: 벤치마크 실행기
- **`run_benchmark.py`**: 메인 스크립트
- 결과: `report/` 폴더에 마크다운으로 자동 생성

### 설정 파일

- **`pyproject.toml`**: 패키지 설정 (PEP 621)
  - 버전: 1.0.2
  - Python: >=3.7
  - 의존성: 없음 (순수 Python)
- **`MANIFEST.in`**: 배포 파일 제어
- **`LICENSE`**: MIT 라이센스
- **`DATA_LICENSE.md`**: AI허브 데이터 라이센스

### 문서

- **`README.md`**: 프로젝트 소개, 사용법
- **`BUILD_GUIDE.md`**: 로컬 빌드 가이드
- **`UPLOAD_GUIDE.md`**: PyPI 업로드 상세 가이드
- **`STRUCTURE.md`**: 이 문서

### 스크립트

- **`upload_jaso_jamo.py`**: PyPI/TestPyPI 업로드 자동화

## 사용 흐름

### 1. 설치

```bash
# PyPI에서 설치
pip install jaso-jamo

# TestPyPI에서 설치
pip install --index-url https://test.pypi.org/simple/ jaso-jamo

# 개발 모드 설치
git clone https://github.com/c0z0c/jaso-jamo.git
cd jaso-jamo
pip install -e .
```

### 2. 라이브러리 사용

```python
from jaso_jamo import tokenize, detokenize

# 자소 분리
text = "안녕하세요"
tokens = tokenize(text)
print(tokens)  # ['ㅇ', 'ㅏ', 'ㄴ', 'ㄴ', 'ㅕ', 'ㅇ', ...]

# 자소 복원
restored = detokenize(tokens)
print(restored)  # "안녕하세요"
```

### 3. 테스트 실행

```bash
python tests/test_basic.py
python tests/test_edge_cases.py
python tests/test_jongseong.py
python tests/test_slang_boundary.py

# 또는 pytest
pytest tests/ -v
```

### 4. 벤치마크 실행

```bash
python benchmarks/run_benchmark.py
# → report/YYYYMMDD_HHMMSS_benchmark_report.md 생성
```

### 5. 빌드 및 배포

```bash
# 빌드
python -m build

# TestPyPI 업로드
python upload_jaso_jamo.py --test

# PyPI 업로드
python upload_jaso_jamo.py
```

## PyPI 배포 상태

- **패키지명**: jaso-jamo
- **버전**: 1.0.2
- **Python**: >=3.7
- **의존성**: 없음
- **TestPyPI**: ✅ 배포 완료
- **PyPI**: 대기 중

## GitHub 체크리스트

- [x] 표준 Python 패키지 구조
- [x] 핵심 라이브러리 (jaso_jamo/)
- [x] 테스트 코드 (tests/)
- [x] 벤치마크 시스템 (benchmarks/)
- [x] 자동 리포트 생성 (report/)
- [x] .gitignore 설정
- [x] pyproject.toml 패키지 설정 (PEP 621)
- [x] MANIFEST.in 배포 파일 제어
- [x] LICENSE 파일 (MIT)
- [x] DATA_LICENSE.md (AI허브)
- [x] README.md
- [x] 문서화 (BUILD_GUIDE, UPLOAD_GUIDE, STRUCTURE)
- [x] GitHub Actions CI/CD
- [x] TestPyPI 배포
- [ ] PyPI 정식 배포
- [ ] GitHub Release

## 다음 단계

1. TestPyPI에서 설치 테스트
2. PyPI 정식 배포 (`python upload_jaso_jamo.py`)
3. GitHub Release 생성 (v1.0.0)
4. 사용 사례 수집
5. 피드백 기반 개선
