"""반복 자소 슬랭 경계 판단 테스트

"바다ㄱㄱ네요" vs "바다ㄱㄱ " 구분 테스트
"""
from jaso_jamo import tokenize, detokenize

def test_slang_boundary():
    """어절 경계에 따른 반복 자소 슬랭 처리 테스트"""
    
    test_cases = [
        # (입력, check_slang_mid=False 기대값, 설명)
        ("바다ㄱㄱ네요", "바닥ㄱ네요", "완성형 한글 뒤: 반복 자소 슬랭 처리 안 함"),
        ("바다ㄱㄱ가요", "바닥ㄱ가요", "완성형 한글 뒤: 반복 자소 슬랭 처리 안 함"),
        ("바다ㄱ이다", "바닥이다", "완성형 한글 뒤: 반복 자소 슬랭 처리 안함"),
        ("바다ㄱㄱ ", "바닥ㄱ ", "공백 뒤: 반복 자소 슬랭 처리 안함"),
        ("바다ㄱㄱ", "바다ㄱㄱ", "단어 끝: 반복 자소 슬랭 처리"),
        ("바다ㄱㄱ!", "바닥ㄱ!", "특수문자 뒤: 반복 자소 슬랭 처리 안함"),
        ("바다ㄱㄱ!가요", "바닥ㄱ!가요", "특수문자 뒤: 반복 자소 슬랭 처리 안함"),
        ("바다ㄱㄱa가요", "바닥ㄱa가요", "영문자 뒤: 반복 자소 슬랭 처리 안함"),
        ("바다ㄱㄱ1234", "바닥ㄱ1234", "숫자 뒤: 반복 자소 슬랭 처리 안함"),
        ("학ㄴ교", "학ㄴ교", "오타 케이스: 반복 자소 슬랭 처리 안 함 (ㄴ은 단일)"),
        ("하ㄱㄱ ", "학ㄱ ", "공백 뒤: 반복 자소 슬랭 처리 안함"),
        ("하ㄱㄱ", "하ㄱㄱ", "단어 끝: 반복 자소 슬랭 처리"),
        ("하ㄱ교", "학교", "완성형 한글 뒤: 반복 자소 슬랭 처리 안 함"),
    ]
    
    print("=" * 80)
    print("반복 자소 슬랭 경계 판단 테스트 (check_slang_mid=False, 기본값)")
    print("=" * 80)
    
    for original, expected, description in test_cases:
        tokens = tokenize(original)
        result = detokenize(tokens, check_slang_mid=False)
        
        status = "✓" if result == expected else "✗"
        
        print(f"\n{status} {description}")
        print(f"  입력: {original}")
        print(f"  토큰: {' '.join(tokens)}")
        print(f"  결과: {result}")
        print(f"  기대: {expected}")
        
        if result != expected:
            print(f"  [FAIL] 불일치!")

if __name__ == "__main__":
    test_slang_boundary()

