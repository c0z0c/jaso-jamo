"""
기존 라이브러리 방식 구현 (공정한 비교)
- unicodedata (Python 표준 라이브러리)
- Greedy 방식 (기준선)
- jamo 라이브러리 (PyPI: jamo)
- hgtk 라이브러리 (PyPI: hgtk)
- hangul-jamo 라이브러리 (PyPI: hangul-jamo)
"""

import unicodedata
from typing import List

# 외부 라이브러리 (선택적 import)
try:
    import jamo

    JAMO_AVAILABLE = True
except ImportError:
    JAMO_AVAILABLE = False

try:
    import hgtk

    HGTK_AVAILABLE = True
except ImportError:
    HGTK_AVAILABLE = False

try:
    from jaso_jamo import compose

    HANGUL_JAMO_AVAILABLE = True
except ImportError:
    HANGUL_JAMO_AVAILABLE = False


class UnicodedataDetokenizer:
    """방법 1: unicodedata.normalize 기반 (표준 라이브러리)

    표준 로직:
    - 자소 위치 기반 호환 자모 → 조합형 자모 변환
    - NFC 정규화로 한글 음절 조합
    """

    def __init__(self):
        # 초성 19자
        self.CHO = [
            "ㄱ",
            "ㄲ",
            "ㄴ",
            "ㄷ",
            "ㄸ",
            "ㄹ",
            "ㅁ",
            "ㅂ",
            "ㅃ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅉ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]
        # 중성 21자
        self.JUNG = [
            "ㅏ",
            "ㅐ",
            "ㅑ",
            "ㅒ",
            "ㅓ",
            "ㅔ",
            "ㅕ",
            "ㅖ",
            "ㅗ",
            "ㅘ",
            "ㅙ",
            "ㅚ",
            "ㅛ",
            "ㅜ",
            "ㅝ",
            "ㅞ",
            "ㅟ",
            "ㅠ",
            "ㅡ",
            "ㅢ",
            "ㅣ",
        ]
        # 종성 27자 (빈 종성 제외)
        self.JONG = [
            "ㄱ",
            "ㄲ",
            "ㄳ",
            "ㄴ",
            "ㄵ",
            "ㄶ",
            "ㄷ",
            "ㄹ",
            "ㄺ",
            "ㄻ",
            "ㄼ",
            "ㄽ",
            "ㄾ",
            "ㄿ",
            "ㅀ",
            "ㅁ",
            "ㅂ",
            "ㅄ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]

        self.CHO_SET = set(self.CHO)
        self.JUNG_SET = set(self.JUNG)
        self.JONG_SET = set(self.JONG)

        # 호환 자모 → 조합형 자모 매핑
        # 초성 (U+3131~ → U+1100~)
        self.CHO_COMPAT_TO_JAMO = {
            "ㄱ": "\u1100",
            "ㄲ": "\u1101",
            "ㄴ": "\u1102",
            "ㄷ": "\u1103",
            "ㄸ": "\u1104",
            "ㄹ": "\u1105",
            "ㅁ": "\u1106",
            "ㅂ": "\u1107",
            "ㅃ": "\u1108",
            "ㅅ": "\u1109",
            "ㅆ": "\u110a",
            "ㅇ": "\u110b",
            "ㅈ": "\u110c",
            "ㅉ": "\u110d",
            "ㅊ": "\u110e",
            "ㅋ": "\u110f",
            "ㅌ": "\u1110",
            "ㅍ": "\u1111",
            "ㅎ": "\u1112",
        }
        # 중성 (U+314F~ → U+1161~)
        self.JUNG_COMPAT_TO_JAMO = {
            "ㅏ": "\u1161",
            "ㅐ": "\u1162",
            "ㅑ": "\u1163",
            "ㅒ": "\u1164",
            "ㅓ": "\u1165",
            "ㅔ": "\u1166",
            "ㅕ": "\u1167",
            "ㅖ": "\u1168",
            "ㅗ": "\u1169",
            "ㅘ": "\u116a",
            "ㅙ": "\u116b",
            "ㅚ": "\u116c",
            "ㅛ": "\u116d",
            "ㅜ": "\u116e",
            "ㅝ": "\u116f",
            "ㅞ": "\u1170",
            "ㅟ": "\u1171",
            "ㅠ": "\u1172",
            "ㅡ": "\u1173",
            "ㅢ": "\u1174",
            "ㅣ": "\u1175",
        }
        # 종성 (U+3131~ → U+11A8~)
        self.JONG_COMPAT_TO_JAMO = {
            "ㄱ": "\u11a8",
            "ㄲ": "\u11a9",
            "ㄳ": "\u11aa",
            "ㄴ": "\u11ab",
            "ㄵ": "\u11ac",
            "ㄶ": "\u11ad",
            "ㄷ": "\u11ae",
            "ㄹ": "\u11af",
            "ㄺ": "\u11b0",
            "ㄻ": "\u11b1",
            "ㄼ": "\u11b2",
            "ㄽ": "\u11b3",
            "ㄾ": "\u11b4",
            "ㄿ": "\u11b5",
            "ㅀ": "\u11b6",
            "ㅁ": "\u11b7",
            "ㅂ": "\u11b8",
            "ㅄ": "\u11b9",
            "ㅅ": "\u11ba",
            "ㅆ": "\u11bb",
            "ㅇ": "\u11bc",
            "ㅈ": "\u11bd",
            "ㅊ": "\u11be",
            "ㅋ": "\u11bf",
            "ㅌ": "\u11c0",
            "ㅍ": "\u11c1",
            "ㅎ": "\u11c2",
        }

    def tokenize(self, text: str) -> List[str]:
        """NFD 정규화로 자모 분해"""
        return list(unicodedata.normalize("NFD", text))

    def detokenize(self, tokens: List[str]) -> str:
        """
        unicodedata.normalize 표준 로직:
        1. 자소 위치 기반 호환 자모 → 조합형 자모 변환
        2. NFC 정규화로 한글 음절 조합

        자소 타입 기반 순차 변환:
        - 초성 위치: 초성 조합형 자모 (U+1100~)
        - 중성 위치: 중성 조합형 자모 (U+1161~)
        - 종성 위치: 종성 조합형 자모 (U+11A8~)
        - 분리된 자음: 호환 자모 유지 (조합 안 함)
        """
        jamo_chars = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # 초성으로 시작
            if token in self.CHO_SET:
                # 다음이 중성인지 확인
                if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                    # 초성 조합형 자모로 변환
                    jamo_chars.append(self.CHO_COMPAT_TO_JAMO[token])
                    i += 1

                    # 중성 조합형 자모로 변환
                    jamo_chars.append(self.JUNG_COMPAT_TO_JAMO[tokens[i]])
                    i += 1

                    # 종성 확인 (선행 탐색: 다음이 중성이면 종성 아님)
                    if i < len(tokens) and tokens[i] in self.JONG_SET:
                        if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                            # 다음이 중성이면 종성이 아니라 다음 음절의 초성
                            pass
                        else:
                            # 종성 조합형 자모로 변환
                            jamo_chars.append(self.JONG_COMPAT_TO_JAMO[tokens[i]])
                            i += 1
                else:
                    # 중성 없음 → 분리된 자음, 호환 자모 유지
                    jamo_chars.append(token)
                    i += 1

            # 중성으로 시작 (초성 없는 경우)
            elif token in self.JUNG_SET:
                # ㅇ 초성 추가
                jamo_chars.append(self.CHO_COMPAT_TO_JAMO["ㅇ"])
                # 중성 조합형 자모로 변환
                jamo_chars.append(self.JUNG_COMPAT_TO_JAMO[token])
                i += 1

                # 종성 확인 (선행 탐색)
                if i < len(tokens) and tokens[i] in self.JONG_SET:
                    if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                        # 다음이 중성이면 종성이 아님
                        pass
                    else:
                        # 종성 조합형 자모로 변환
                        jamo_chars.append(self.JONG_COMPAT_TO_JAMO[tokens[i]])
                        i += 1

            # 종성으로 시작 (초성·중성 없는 경우)
            elif token in self.JONG_SET:
                # 분리된 자음 - 호환 자모 그대로 유지
                jamo_chars.append(token)
                i += 1

            # 한글 자모가 아닌 경우 (공백, 구두점 등)
            else:
                jamo_chars.append(token)
                i += 1

        jamo_str = "".join(jamo_chars)
        # NFC 정규화로 조합
        return unicodedata.normalize("NFC", jamo_str)


class GreedyDetokenizer:
    """방법 2: Greedy 방식 (표준 자소 타입 기반 순차 결합 - 기준선)"""

    def __init__(self):
        # 초성 19자
        self.CHO = [
            "ㄱ",
            "ㄲ",
            "ㄴ",
            "ㄷ",
            "ㄸ",
            "ㄹ",
            "ㅁ",
            "ㅂ",
            "ㅃ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅉ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]
        # 중성 21자
        self.JUNG = [
            "ㅏ",
            "ㅐ",
            "ㅑ",
            "ㅒ",
            "ㅓ",
            "ㅔ",
            "ㅕ",
            "ㅖ",
            "ㅗ",
            "ㅘ",
            "ㅙ",
            "ㅚ",
            "ㅛ",
            "ㅜ",
            "ㅝ",
            "ㅞ",
            "ㅟ",
            "ㅠ",
            "ㅡ",
            "ㅢ",
            "ㅣ",
        ]
        # 종성 28자 (빈 종성 포함)
        self.JONG = [
            "",
            "ㄱ",
            "ㄲ",
            "ㄳ",
            "ㄴ",
            "ㄵ",
            "ㄶ",
            "ㄷ",
            "ㄹ",
            "ㄺ",
            "ㄻ",
            "ㄼ",
            "ㄽ",
            "ㄾ",
            "ㄿ",
            "ㅀ",
            "ㅁ",
            "ㅂ",
            "ㅄ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]

        self.CHO_SET = set(self.CHO)
        self.JUNG_SET = set(self.JUNG)
        self.JONG_SET = set(self.JONG[1:])

    def tokenize(self, text: str) -> List[str]:
        """NFD 정규화로 자모 분해"""
        return list(unicodedata.normalize("NFD", text))

    def detokenize(self, tokens: List[str]) -> str:
        """
        표준 Greedy 전략: 자소 타입 기반 순차 결합
        1. 초성(CHO) 발견 → 새 음절 시작
        2. 중성(JUNG) 발견 → 현재 음절에 추가 (초성 필요)
        3. 종성(JONG) 발견 → 현재 음절에 추가 (초성+중성 필요)
        4. 결합 불가 → 이전 음절 완성, 자소 그대로 출력
        """
        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # 초성으로 시작
            if token in self.CHO_SET:
                cho = token
                jung = ""
                jong = ""
                i += 1

                # 다음이 중성인지 확인
                if i < len(tokens) and tokens[i] in self.JUNG_SET:
                    jung = tokens[i]
                    i += 1

                    # 다음이 종성인지 확인
                    if i < len(tokens) and tokens[i] in self.JONG_SET:
                        # 종성 후보
                        jong_candidate = tokens[i]

                        # 다음 토큰이 중성이면 종성이 아니라 다음 음절의 초성
                        if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                            # 종성을 초성으로 사용 가능한지 확인
                            if jong_candidate in self.CHO_SET:
                                # 종성 없이 완성
                                char = self._compose(cho, jung, "")
                                result.append(char)
                                continue

                        # 종성으로 확정
                        jong = jong_candidate
                        i += 1

                    # 음절 완성
                    char = self._compose(cho, jung, jong)
                    result.append(char)
                else:
                    # 중성 없음 → 초성 그대로
                    result.append(cho)

            # 중성 단독
            elif token in self.JUNG_SET:
                result.append(token)
                i += 1

            # 종성 단독 (초성으로도 사용 가능)
            elif token in self.JONG_SET:
                result.append(token)
                i += 1

            # 기타 문자
            else:
                result.append(token)
                i += 1

        return "".join(result)

    def _compose(self, cho: str, jung: str, jong: str = "") -> str:
        """자소 조합하여 음절 생성"""
        if not cho or not jung:
            return cho + jung + jong

        if cho not in self.CHO_SET or jung not in self.JUNG_SET:
            return cho + jung + jong

        if jong and jong not in self.JONG_SET:
            return cho + jung + jong

        cho_idx = self.CHO.index(cho)
        jung_idx = self.JUNG.index(jung)
        jong_idx = self.JONG.index(jong) if jong else 0

        code = 0xAC00 + (cho_idx * 21 + jung_idx) * 28 + jong_idx
        return chr(code)


class JamoLibraryDetokenizer:
    """방법 3: jamo 라이브러리 (PyPI: jamo)

    설치: pip install jamo
    특징: 가장 널리 사용되는 한글 자모 처리 라이브러리
    GitHub: https://github.com/JDongian/python-jamo
    Python 3.10 호환: O

    표준 API: jamo.jamo_to_hangul(lead, vowel, tail='') 사용
    - HCJ (compatible jamo) 입력 지원
    """

    def __init__(self):
        # 초성 19자
        self.CHO = [
            "ㄱ",
            "ㄲ",
            "ㄴ",
            "ㄷ",
            "ㄸ",
            "ㄹ",
            "ㅁ",
            "ㅂ",
            "ㅃ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅉ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]
        # 중성 21자
        self.JUNG = [
            "ㅏ",
            "ㅐ",
            "ㅑ",
            "ㅒ",
            "ㅓ",
            "ㅔ",
            "ㅕ",
            "ㅖ",
            "ㅗ",
            "ㅘ",
            "ㅙ",
            "ㅚ",
            "ㅛ",
            "ㅜ",
            "ㅝ",
            "ㅞ",
            "ㅟ",
            "ㅠ",
            "ㅡ",
            "ㅢ",
            "ㅣ",
        ]
        # 종성 27자 (빈 종성 제외)
        self.JONG = [
            "ㄱ",
            "ㄲ",
            "ㄳ",
            "ㄴ",
            "ㄵ",
            "ㄶ",
            "ㄷ",
            "ㄹ",
            "ㄺ",
            "ㄻ",
            "ㄼ",
            "ㄽ",
            "ㄾ",
            "ㄿ",
            "ㅀ",
            "ㅁ",
            "ㅂ",
            "ㅄ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]

        self.CHO_SET = set(self.CHO)
        self.JUNG_SET = set(self.JUNG)
        self.JONG_SET = set(self.JONG)

    def tokenize(self, text: str) -> List[str]:
        """jamo.h2j (hangul to jamo) - 조합형 자모 반환"""
        return list(jamo.h2j(text))

    def detokenize(self, tokens: List[str]) -> str:
        """jamo.jamo_to_hangul(lead, vowel, tail='') 표준 API 사용

        jamo 라이브러리 공식 API:
        - jamo_to_hangul(lead, vowel, tail=''): 자모 3개를 한글로 변환
        - HCJ (compatible jamo) 입력 지원

        표준 로직:
        - 자소 타입 기반 순차 결합
        - 종성 후보 선행 탐색 (다음이 중성이면 종성 X)
        """
        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # 초성으로 시작
            if token in self.CHO_SET:
                cho = token
                jung = ""
                jong = ""

                # 다음 토큰이 중성인지 확인
                if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                    jung = tokens[i + 1]
                    i += 2

                    # 종성 확인 (선행 탐색: 다음이 중성이면 종성 아님)
                    if i < len(tokens) and tokens[i] in self.JONG_SET:
                        # 다음 토큰이 중성인지 확인
                        if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                            # 다음이 중성이면 종성이 아니라 다음 음절의 초성
                            pass
                        else:
                            jong = tokens[i]
                            i += 1

                    # jamo_to_hangul(cho, jung, jong) 호출
                    try:
                        if jong:
                            result.append(jamo.jamo_to_hangul(cho, jung, jong))
                        else:
                            result.append(jamo.jamo_to_hangul(cho, jung))
                    except:
                        # 변환 실패 시 원본 자모 유지
                        result.extend([cho, jung] + ([jong] if jong else []))
                else:
                    # 중성이 없으면 초성만
                    result.append(cho)
                    i += 1

            # 중성으로 시작 (초성 없는 경우)
            elif token in self.JUNG_SET:
                jung = token
                jong = ""
                i += 1  # 중성 토큰 소비

                # 종성 확인 (선행 탐색: 다음이 중성이면 종성 아님)
                if i < len(tokens) and tokens[i] in self.JONG_SET:
                    # 다음 토큰이 중성인지 확인
                    if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                        # 다음이 중성이면 종성이 아니라 다음 음절의 초성
                        pass
                    else:
                        jong = tokens[i]
                        i += 1

                # 'ㅇ' 초성으로 조합
                try:
                    if jong:
                        result.append(jamo.jamo_to_hangul("ㅇ", jung, jong))
                    else:
                        result.append(jamo.jamo_to_hangul("ㅇ", jung))
                except:
                    result.extend([jung] + ([jong] if jong else []))

            # 종성으로 시작 (초성·중성 없는 경우)
            elif token in self.JONG_SET:
                result.append(token)
                i += 1

            # 한글 자모가 아닌 경우 (공백, 구두점 등)
            else:
                result.append(token)
                i += 1

        return "".join(result)


class HgtkDetokenizer:
    """방법 4: hgtk 라이브러리 (PyPI: hgtk)

    설치: pip install hgtk
    특징: Hangul Toolkit - 한글 자모 분리/결합 전문 라이브러리
    GitHub: https://github.com/bluedisk/hangul-toolkit
    Python 3.10 호환: O
    """

    def __init__(self):
        # 초성 19자
        self.CHO = [
            "ㄱ",
            "ㄲ",
            "ㄴ",
            "ㄷ",
            "ㄸ",
            "ㄹ",
            "ㅁ",
            "ㅂ",
            "ㅃ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅉ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]
        # 중성 21자
        self.JUNG = [
            "ㅏ",
            "ㅐ",
            "ㅑ",
            "ㅒ",
            "ㅓ",
            "ㅔ",
            "ㅕ",
            "ㅖ",
            "ㅗ",
            "ㅘ",
            "ㅙ",
            "ㅚ",
            "ㅛ",
            "ㅜ",
            "ㅝ",
            "ㅞ",
            "ㅟ",
            "ㅠ",
            "ㅡ",
            "ㅢ",
            "ㅣ",
        ]
        # 종성 27자 (빈 종성 제외)
        self.JONG = [
            "ㄱ",
            "ㄲ",
            "ㄳ",
            "ㄴ",
            "ㄵ",
            "ㄶ",
            "ㄷ",
            "ㄹ",
            "ㄺ",
            "ㄻ",
            "ㄼ",
            "ㄽ",
            "ㄾ",
            "ㄿ",
            "ㅀ",
            "ㅁ",
            "ㅂ",
            "ㅄ",
            "ㅅ",
            "ㅆ",
            "ㅇ",
            "ㅈ",
            "ㅊ",
            "ㅋ",
            "ㅌ",
            "ㅍ",
            "ㅎ",
        ]

        self.CHO_SET = set(self.CHO)
        self.JUNG_SET = set(self.JUNG)
        self.JONG_SET = set(self.JONG)

    def tokenize(self, text: str) -> List[str]:
        """hgtk.letter.decompose로 자모 분해"""
        result = []
        for char in text:
            if hgtk.checker.is_hangul(char):
                decomposed = hgtk.letter.decompose(char)
                result.extend(list(decomposed))
            else:
                result.append(char)
        return result

    def detokenize(self, tokens: List[str]) -> str:
        """
        hgtk.letter.compose로 자모 조합 (표준 로직)
        자소 타입 기반 순차 결합
        """
        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # 초성으로 시작
            if token in self.CHO_SET:
                cho = token
                jung = ""
                jong = ""
                i += 1

                # 다음이 중성인지 확인
                if i < len(tokens) and tokens[i] in self.JUNG_SET:
                    jung = tokens[i]
                    i += 1

                    # 다음이 종성인지 확인
                    if i < len(tokens) and tokens[i] in self.JONG_SET:
                        jong_candidate = tokens[i]

                        # 다음 토큰이 중성이면 종성이 아니라 다음 음절의 초성
                        if i + 1 < len(tokens) and tokens[i + 1] in self.JUNG_SET:
                            if jong_candidate in self.CHO_SET:
                                # 종성 없이 완성
                                try:
                                    char = hgtk.letter.compose(cho, jung)
                                    result.append(char)
                                except:
                                    result.append(cho + jung)
                                continue

                        # 종성으로 확정
                        jong = jong_candidate
                        i += 1

                    # 음절 완성
                    try:
                        if jong:
                            char = hgtk.letter.compose(cho, jung, jong)
                        else:
                            char = hgtk.letter.compose(cho, jung)
                        result.append(char)
                    except:
                        result.append(cho + jung + jong)
                else:
                    # 중성 없음 → 초성 그대로
                    result.append(cho)

            # 중성 단독
            elif token in self.JUNG_SET:
                result.append(token)
                i += 1

            # 종성 단독 (초성으로도 사용 가능)
            elif token in self.JONG_SET:
                result.append(token)
                i += 1

            # 기타 문자
            else:
                result.append(token)
                i += 1

        return "".join(result)


class HangulJamoDetokenizer:
    """방법 5: hangul-jamo 라이브러리 (PyPI: hangul-jamo)

    설치: pip install hangul-jamo
    특징: 순수 Python 구현, 간단한 API
    GitHub: https://github.com/kaniblu/hangul-jamo
    Python 3.10 호환: O
    """

    def __init__(self):
        pass  # 선택적 import는 run_benchmark.py에서 처리

    def tokenize(self, text: str) -> List[str]:
        """NFD 정규화로 자모 분해"""
        return list(unicodedata.normalize("NFD", text))

    def detokenize(self, tokens: List[str]) -> str:
        """hangul_jaso.compose로 자모 조합"""
        jamo_str = "".join(tokens)
        return compose(jamo_str)


# 호환성을 위한 alias
JamoDetokenizer = JamoLibraryDetokenizer


# 사용 가능한 라이브러리 목록
AVAILABLE_DETOKENIZERS = {
    "unicodedata": UnicodedataDetokenizer,
    "greedy": GreedyDetokenizer,
}

if JAMO_AVAILABLE:
    AVAILABLE_DETOKENIZERS["jamo"] = JamoLibraryDetokenizer

if HGTK_AVAILABLE:
    AVAILABLE_DETOKENIZERS["hgtk"] = HgtkDetokenizer

if HANGUL_JAMO_AVAILABLE:
    AVAILABLE_DETOKENIZERS["hangul_jaso"] = HangulJamoDetokenizer
