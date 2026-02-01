"""
엣지 케이스 테스트
"""

import sys
import io
from pathlib import Path

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from jaso_jamo import tokenize, detokenize


def test_slang():
    """반복 자소 슬랭 테스트 (핵심 차별화 기능)"""
    test_cases = [
        "ㅋㅋㅋ",
        "ㅎㅎㅎ",
        "ㄱㄱ",
        "ㅇㅇ",
        "가요ㅋㅋㅋ",
        "네ㅎㅎㅎ",
        "알겠습니다ㅋㅋ",
        "그래요ㅎㅎ",
        "가요ㅋㅋㅋ",
        "가요ㅋㅋ",
        "가요ㄱㄱ",
        "ㅇㅋ가요",
        "네ㅇㅋ",
        "넵ㅇㅋ",
        "냉캄사",
        "자소복원",
    ]

    print("=" * 60)
    print("반복 자소 슬랭 테스트 (핵심 차별화)")
    print("=" * 40)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → {tokens} → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}")
    print(f"정확도: {passed/len(test_cases)*100:.1f}%\n")
    return passed, len(test_cases)


def test_mixed_korean_english():
    """한영 혼용 테스트"""
    test_cases = [
        "Hello 안녕",
        "Python 파이썬",
        "GitHub 공유",
        "NLP 자연어처리",
        "AI 인공지능",
        "Machine Learning 머신러닝",
    ]

    print("=" * 60)
    print("한영 혼용 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}")
    print(f"정확도: {passed/len(test_cases)*100:.1f}%\n")
    return passed, len(test_cases)


def test_special_characters():
    """특수문자 테스트"""
    test_cases = [
        "안녕!",
        "감사합니다.",
        "테스트@#$",
        "숫자123",
        "이모지 없음",
        "괄호(테스트)",
        "물음표?느낌표!",
    ]

    print("=" * 60)
    print("특수문자 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}")
    print(f"정확도: {passed/len(test_cases)*100:.1f}%\n")
    return passed, len(test_cases)


def test_complex_jongseong():
    """복잡한 종성 테스트"""
    test_cases = [
        "값",
        "넓",
        "읊",
        "없",
        "웃",
        "앉",
        "여덟",
        "삶",
        "닮",
        "굵",
        "짧",
        "옳",
    ]

    print("=" * 60)
    print("복잡한 종성 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        print(f"{status} '{text}' → {tokens} → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}")
    print(f"정확도: {passed/len(test_cases)*100:.1f}%\n")
    return passed, len(test_cases)


def test_empty_and_single():
    """빈 문자열 및 단일 문자 테스트"""
    test_cases = [
        "",
        "가",
        "ㄱ",
        "ㅏ",
        "a",
        "1",
        " ",
    ]

    print("=" * 60)
    print("빈 문자열 및 단일 문자 테스트")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        tokens = tokenize(text)
        restored = detokenize(tokens)
        status = "v" if text == restored else "❌"
        display = repr(text) if text in ["", " "] else text
        print(f"{status} {display} → {tokens} → '{restored}'")
        if text == restored:
            passed += 1

    print(f"\n통과: {passed}/{len(test_cases)}")
    print(f"정확도: {passed/len(test_cases)*100:.1f}%\n")
    return passed, len(test_cases)


def main():
    """모든 엣지 케이스 테스트 실행"""
    print("\n" + "=" * 60)
    print("한글 자소 복원 엣지 케이스 테스트")
    print("=" * 60 + "\n")

    results = []
    results.append(("반복 자소 슬랭", test_slang()))
    results.append(("한영 혼용", test_mixed_korean_english()))
    results.append(("특수문자", test_special_characters()))
    results.append(("복잡한 종성", test_complex_jongseong()))
    results.append(("빈 문자열/단일", test_empty_and_single()))

    print("=" * 60)
    print("전체 결과")
    print("=" * 60)

    total_passed = 0
    total_cases = 0

    for name, (passed, total) in results:
        accuracy = passed / total * 100 if total > 0 else 0
        status = "v" if passed == total else "⚠️"
        print(f"{status} {name}: {passed}/{total} ({accuracy:.1f}%)")
        total_passed += passed
        total_cases += total

    overall_accuracy = total_passed / total_cases * 100 if total_cases > 0 else 0

    print("\n" + "=" * 60)
    print(f"전체 정확도: {total_passed}/{total_cases} ({overall_accuracy:.2f}%)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
