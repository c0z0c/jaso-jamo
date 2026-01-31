"""
기본 테스트 케이스
"""

import sys
import io
from pathlib import Path

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from jaso_jamo import tokenize, detokenize


def test_basic_words():
    """기본 단어 테스트"""
    test_cases = [
        "한글",
        "안녕",
        "감사",
        "사랑",
        "행복",
    ]

    print("=" * 60)
    print("기본 단어 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → {tokens} → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}\n")
    return passed == len(test_cases)


def test_jongseong():
    """종성 테스트"""
    test_cases = [
        "각",
        "간",
        "갈",
        "감",
        "갑",
        "갓",
        "강",
        "국",
        "굳",
        "굴",
        "굼",
        "굽",
        "밝",
        "닭",
        "삶",
        "앞",
        "옆",
    ]

    print("=" * 60)
    print("종성 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → {tokens} → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}\n")
    return passed == len(test_cases)


def test_long_sentences():
    """긴 문장 테스트"""
    test_cases = [
        "안녕하세요",
        "감사합니다",
        "반갑습니다",
        "한글 자소 분리와 복원",
        "자연어 처리 라이브러리",
        "5단계 Fallback 알고리즘을 적용하였습니다",
    ]

    print("=" * 60)
    print("긴 문장 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text[:30]}...' → '{restored[:30]}...'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}\n")
    return passed == len(test_cases)


def main():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("한글 자소 복원 기본 테스트")
    print("=" * 60 + "\n")

    results = []
    results.append(("기본 단어", test_basic_words()))
    results.append(("종성", test_jongseong()))
    results.append(("긴 문장", test_long_sentences()))

    print("=" * 60)
    print("전체 결과")
    print("=" * 60)

    for name, passed in results:
        status = "v PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 모든 테스트 통과!" if all_passed else "⚠️ 일부 테스트 실패"))
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
