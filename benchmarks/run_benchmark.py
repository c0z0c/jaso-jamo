"""
벤치마크 실행 스크립트
제안 방식 vs 기존 라이브러리 성능 비교
"""

import sys
import io
import time
import math
import random
import argparse
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from jaso_jamo import tokenize, detokenize
from benchmarks.baseline_libraries import (
    UnicodedataDetokenizer,
    GreedyDetokenizer,
)

# 선택적 라이브러리 import
try:
    from benchmarks.baseline_libraries import JamoDetokenizer

    HAS_JAMO = True
except ImportError:
    HAS_JAMO = False

try:
    from benchmarks.baseline_libraries import HangulUtilsDetokenizer

    HAS_HANGUL_UTILS = True
except ImportError:
    HAS_HANGUL_UTILS = False

try:
    from benchmarks.baseline_libraries import KoreanLibraryDetokenizer

    HAS_KOREAN = True
except ImportError:
    HAS_KOREAN = False


class BenchmarkRunner:
    """벤치마크 실행기"""

    def __init__(self):
        self.jaso_jamo = None  # 함수 기반으로 사용
        self.unicodedata = UnicodedataDetokenizer()
        self.greedy = GreedyDetokenizer()

        # 선택적 라이브러리 초기화
        self.jamo_lib = JamoDetokenizer() if HAS_JAMO else None
        self.hangul_utils = HangulUtilsDetokenizer() if HAS_HANGUL_UTILS else None
        self.korean_lib = KoreanLibraryDetokenizer() if HAS_KOREAN else None

        # 사용 가능한 메서드만 포함
        self.method_names = {
            "jaso_jamo": "jaso_jamo 라이브러리",
            "unicodedata": "unicodedata (표준 라이브러리)",
            "greedy": "Greedy 방식 (기준선)",
        }

        if HAS_JAMO:
            self.method_names["jamo"] = "jamo 라이브러리"
        if HAS_HANGUL_UTILS:
            self.method_names["hangul_utils"] = "hangul-utils 라이브러리"
        if HAS_KOREAN:
            self.method_names["korean"] = "korean 라이브러리"

        # 사용 가능한 메서드 키 목록
        self.available_methods = list(self.method_names.keys())

    def run_combined_test(self, test_cases: List[str], iterations: int = 3) -> tuple:
        """정확도와 속도를 동시에 측정"""
        accuracy_results = {}
        speed_results = {}

        for method_key in self.available_methods:
            correct = 0
            total = len(test_cases)
            errors = []
            times = []

            desc = f"테스트: {self.method_names[method_key]}"
            total_ops = iterations * len(test_cases)

            with tqdm(total=total_ops, desc=desc, ncols=80) as pbar:
                for iteration in range(iterations):
                    start = time.time()

                    for i, original in enumerate(test_cases):
                        try:
                            # 자소 분리
                            tokens = tokenize(original)

                            # 복원
                            restored = None
                            if method_key == "jaso_jamo":
                                restored = detokenize(tokens)
                            elif method_key == "unicodedata":
                                restored = self.unicodedata.detokenize(tokens)
                            elif method_key == "greedy":
                                restored = self.greedy.detokenize(tokens)
                            elif method_key == "jamo" and self.jamo_lib:
                                restored = self.jamo_lib.detokenize(tokens)
                            elif method_key == "hangul_utils" and self.hangul_utils:
                                restored = self.hangul_utils.detokenize(tokens)
                            elif method_key == "korean" and self.korean_lib:
                                restored = self.korean_lib.detokenize(tokens)

                            # 첫 iteration에서만 정확도 측정
                            if iteration == 0:
                                if restored is not None and restored == original:
                                    correct += 1
                                else:
                                    errors.append(
                                        {
                                            "index": i,
                                            "original": original,
                                            "tokens": tokens,
                                            "restored": restored,
                                        }
                                    )
                        except Exception as e:
                            if iteration == 0:
                                errors.append(
                                    {
                                        "index": i,
                                        "original": original,
                                        "error": str(e),
                                    }
                                )

                        pbar.update(1)

                    elapsed = time.time() - start
                    times.append(elapsed)

            # 정확도 결과
            accuracy = (correct / total * 100) if total > 0 else 0
            accuracy_results[method_key] = {
                "correct": correct,
                "total": total,
                "accuracy": accuracy,
                "errors": errors,
            }

            # 속도 결과
            speed_results[method_key] = {
                "mean": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
            }

        return accuracy_results, speed_results

    def generate_markdown_report(
        self,
        accuracy_results: Dict,
        speed_results: Dict,
        test_cases: List[str],
        output_path: str,
        test_file_name: str,
    ):
        """마크다운 리포트 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# 한글 자소 복원 벤치마크 리포트

**생성 시간**: {timestamp}
**테스트 데이터**: {test_file_name}
**테스트 샘플 수**: {len(test_cases):,}개

---

## 1. 정확도 비교

| 순위 | 방식 | 정확도 | 정답/전체 | 에러 수 |
|------|------|--------|-----------|---------|
"""

        # 정확도 순위
        acc_ranking = sorted(
            accuracy_results.items(), key=lambda x: x[1]["accuracy"], reverse=True
        )

        for rank, (method_key, result) in enumerate(acc_ranking, 1):
            accuracy_truncated = math.floor(result["accuracy"] * 1000) / 1000
            report += f"| {rank} | {self.method_names[method_key]} | "
            report += f"{accuracy_truncated:.3f}% | "
            report += f"{result['correct']}/{result['total']} | "
            report += f"{len(result['errors'])} |\n"

        report += "\n---\n\n## 2. 속도 비교\n\n"
        report += "| 순위 | 방식 | 평균 시간 (ms) | 처리량 (samples/s) |\n"
        report += "|------|------|----------------|-------------------|\n"

        # 속도 순위
        speed_ranking = sorted(speed_results.items(), key=lambda x: x[1]["mean"])

        for rank, (method_key, result) in enumerate(speed_ranking, 1):
            # 밀리초 변환
            mean_ms = result["mean"] * 1000
            time_str = (
                f"{math.floor(mean_ms * 1000) / 1000:.3f}"
                if mean_ms >= 0.01
                else "< 0.01"
            )

            # 처리량 계산
            if result["mean"] > 0:
                throughput = len(test_cases) / result["mean"]
                throughput_str = f"{math.floor(throughput * 1000) / 1000:,.3f}"
            else:
                throughput_str = "> 1,000,000"

            report += f"| {rank} | {self.method_names[method_key]} | "
            report += f"{time_str} | "
            report += f"{throughput_str} |\n"

        report += "\n---\n\n## 3. 상세 분석\n\n"

        # jaso_jamo 방식의 우수성
        jaso_jamo_acc = accuracy_results["jaso_jamo"]["accuracy"]
        best_baseline = max(
            [(k, v) for k, v in accuracy_results.items() if k != "jaso_jamo"],
            key=lambda x: x[1]["accuracy"],
        )
        improvement = jaso_jamo_acc - best_baseline[1]["accuracy"]

        report += f"### 3.1 정확도 개선\n\n"
        jaso_jamo_acc_truncated = math.floor(jaso_jamo_acc * 1000) / 1000
        best_acc_truncated = math.floor(best_baseline[1]["accuracy"] * 1000) / 1000
        improvement_truncated = math.floor(improvement * 1000) / 1000
        report += f"- **jaso_jamo 방식**: {jaso_jamo_acc_truncated:.3f}%\n"
        report += f"- **최고 기존 방식** ({self.method_names[best_baseline[0]]}): {best_acc_truncated:.3f}%\n"
        report += f"- **개선율**: {improvement_truncated:+.3f}%p\n\n"

        # 에러 케이스 분석
        report += "### 3.2 jaso_jamo 방식 에러 케이스 (최대 10개)\n\n"

        jaso_jamo_errors = accuracy_results["jaso_jamo"]["errors"]
        if jaso_jamo_errors:
            for i, error in enumerate(jaso_jamo_errors[:10], 1):
                original = error.get("original", "N/A")
                tokens = " ".join(error.get("tokens", []))
                restored = error.get("restored", error.get("error", "ERROR"))

                report += f"#### 에러 케이스 #{i}\n\n"
                report += f"**원본**\n```\n{original}\n```\n\n"
                report += f"**자모 분리**\n```\n{tokens}\n```\n\n"
                report += f"**복원 결과**\n```\n{restored}\n```\n\n"
                report += "---\n\n"

            if len(jaso_jamo_errors) > 10:
                report += f"\n*... 외 {len(jaso_jamo_errors) - 10}개 더 있음*\n"
        else:
            report += "**모든 테스트 케이스 통과! 완벽한 정확도!**\n"

        report += "\n---\n\n## 4. 테스트 데이터 샘플 (처음 20개)\n\n"
        report += "| # | 텍스트 | 길이 |\n"
        report += "|---|--------|------|\n"

        for i, text in enumerate(test_cases[:20], 1):
            report += f"| {i} | {text} | {len(text)} |\n"

        if len(test_cases) > 20:
            report += f"\n*... 외 {len(test_cases) - 20}개 더 있음*\n"

        report += "\n---\n\n## 5. 결론\n\n"

        # if improvement > 5:
        #     conclusion = "**제안 방식이 기존 방식 대비 압도적으로 우수합니다!**"
        # elif improvement > 1:
        #     conclusion = "**제안 방식이 기존 방식 대비 유의미하게 개선되었습니다.**"
        # elif improvement > 0:
        #     conclusion = "제안 방식이 기존 방식 대비 소폭 개선되었습니다."
        # else:
        #     conclusion = "개선이 필요합니다."
        # report += f"{conclusion}\n\n"

        report += f"\n\n"
        report += f"- 정확도 개선: {improvement:+.2f}%p\n"
        report += f"- 에러 감소: {len(best_baseline[1]['errors']) - len(jaso_jamo_errors)}개\n"

        # 파일 저장
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n리포트 저장: {output_path}")

        # 에러 리포트 생성
        report_dir = Path(output_path).parent
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        for method_key, result in accuracy_results.items():
            errors = result["errors"]
            if not errors:
                continue

            error_report = f"""# {self.method_names[method_key]} 에러 리포트

**생성 시간**: {timestamp}
**에러 수**: {len(errors)}개
**샘플 수**: 최대 10개

---

"""

            for i, error in enumerate(errors[:10], 1):
                original = error.get("original", "N/A")
                tokens = " ".join(error.get("tokens", []))
                restored = error.get("restored", error.get("error", "ERROR"))

                error_report += f"## 에러 케이스 #{i}\n\n"
                error_report += f"**원본**\n```\n{original}\n```\n\n"
                error_report += f"**자모 분리**\n```\n{tokens}\n```\n\n"
                error_report += f"**복원 결과**\n```\n{restored}\n```\n\n"
                error_report += "---\n\n"

            error_file = report_dir / f"{timestamp_str}_error_report_{method_key}.md"
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(error_report)

            print(f"에러 리포트 저장: {error_file}")


def load_test_cases(file_path: str, sample_size: int = 0) -> List[str]:
    """
    테스트 케이스 파일을 읽어옵니다.

    Args:
        file_path: 테스트 케이스 파일 경로
        sample_size: 샘플 크기 (0이면 전체 사용)

    Returns:
        테스트 케이스 리스트
    """
    test_cases = []

    try:
        print(f"테스트 케이스 로드 중: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 텍스트를 문장 단위로 분리 (줄바꿈, 마침표, 느낌표, 물음표 기준)
        import re

        sentences = re.split(r"[\n.!?]+", content)

        # 빈 문장 제거 및 공백 정리
        test_cases = [s.strip() for s in sentences if s.strip()]

        total_count = len(test_cases)
        print(f"전체 문장 수: {total_count:,}개")

        # 샘플링
        if sample_size > 0 and sample_size < total_count:
            print(f"랜덤 샘플링: {sample_size:,}개")
            test_cases = random.sample(test_cases, sample_size)
        elif sample_size > 0:
            print(
                f"경고: 요청 샘플 수({sample_size:,})가 전체({total_count:,})보다 많습니다. 전체를 사용합니다."
            )

        print(f"테스트 케이스 로드 완료: {len(test_cases):,}개")
        return test_cases

    except FileNotFoundError:
        print(
            f"경고: {file_path} 파일을 찾을 수 없습니다. 기본 테스트 케이스를 사용합니다."
        )
        return [
            "한글",
            "안녕하세요",
            "감사합니다",
            "자소분리",
            "각",
            "국",
            "밝",
            "닭",
            "삶",
            "ㅋㅋㅋ",
            "ㅎㅎㅎ",
            "ㄱㄱ",
            "ㅇㅇ",
        ]
    except Exception as e:
        print(f"오류: 테스트 케이스 로드 실패 - {e}")
        return []


def main():
    """메인 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="한글 자소 복원 벤치마크")
    parser.add_argument(
        "--input", type=str, default="test_cases.txt", help="테스트 케이스 파일 경로"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="테스트 샘플 수 (0: 전체, n: n개 랜덤 샘플링)",
    )
    parser.add_argument(
        "--iterations", type=int, default=1, help="속도 테스트 반복 횟수"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("한글 자소 복원 벤치마크 시스템")
    print("=" * 60)

    # 테스트 케이스 로드
    test_case_file = Path(args.input)
    if not test_case_file.is_absolute():
        test_case_file = Path(__file__).parent / args.input
        if not test_case_file.exists():
            test_case_file = Path(__file__).parent.parent / ".data" / args.input

    if not Path(test_case_file).exists():
        print(
            f"경고: {test_case_file} 파일을 찾을 수 없습니다. 기본 테스트 케이스를 사용합니다."
        )
        return

    test_cases = load_test_cases(str(test_case_file), sample_size=args.sample)

    if not test_cases:
        print("오류: 테스트 케이스가 없습니다.")
        return

    # 벤치마크 실행
    runner = BenchmarkRunner()

    print("\n정확도 및 속도 테스트 실행 중...")
    accuracy_results, speed_results = runner.run_combined_test(
        test_cases, iterations=args.iterations
    )

    print("\n리포트 생성 중...")

    # report 폴더 생성
    report_dir = Path(__file__).parent.parent / "report"
    report_dir.mkdir(exist_ok=True)

    # 타임스탬프로 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_suffix = f"_sample{args.sample}" if args.sample > 0 else "_full"
    output_path = report_dir / f"{timestamp}_benchmark_report.md"

    runner.generate_markdown_report(
        accuracy_results,
        speed_results,
        test_cases,
        str(output_path),
        test_case_file.name,
    )

    # 결과 출력
    print("\n" + "=" * 60)
    print("벤치마크 결과 요약")
    print("=" * 60)

    for method_key in runner.available_methods:
        acc = accuracy_results[method_key]["accuracy"]
        print(f"\n{runner.method_names[method_key]}")
        print(f"  정확도: {acc:.2f}%")
        print(f"  에러: {len(accuracy_results[method_key]['errors'])}개")

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
