"""
겹받침 자소 분리 테스트
"""
import sys
from pathlib import Path
# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from jaso_jamo.JasoJamoTokenizer import JasoJamoTokenizer

# 겹받침 테스트
tokenizer = JasoJamoTokenizer()

test_words = ["닭", "값", "없다", "빨강", "밟다", "넓다", "읽다", "삶"]

print("=" * 60)
print("겹받침 자소 분리 테스트")
print("=" * 60)

for word in test_words:
    tokens = tokenizer.tokenize(word)
    print(f"{word:6s} → {tokens}")
    print(f"       → {' '.join(tokens)}")

    # 유니코드 확인
    for char in word:
        if 0xAC00 <= ord(char) <= 0xD7A3:
            code = ord(char) - 0xAC00
            jong_idx = code % 28
            jung_idx = ((code - jong_idx) // 28) % 21
            cho_idx = ((code - jong_idx) // 28) // 21
            print(
                f"       [유니코드: {hex(ord(char))}, 초성:{cho_idx}, 중성:{jung_idx}, 종성:{jong_idx}]"
            )
    print()
