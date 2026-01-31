"""
공통 벤치마크 러너 기본 클래스
모든 벤치마크가 상속받아 사용
"""

import time
from typing import List, Dict, Callable, Tuple
from datetime import datetime
from pathlib import Path

from benchmarks.benchmark_record import BenchmarkRecord, MethodBenchmarkResult


class BaseBenchmarkRunner:
    """벤치마크 실행 기본 클래스"""

    def __init__(self):
        self.methods: Dict[str, Tuple[Callable, Callable]] = {}
        self.method_names: Dict[str, str] = {}
        self.results: Dict[str, MethodBenchmarkResult] = {}

    def register_method(
        self, key: str, display_name: str, tokenizer: Callable, detokenizer: Callable
    ):
        """벤치마크 방법 등록"""
        self.methods[key] = (tokenizer, detokenizer)
        self.method_names[key] = display_name

    def run_benchmark(
        self, test_cases: List[str], progress_interval: int = 1000
    ) -> Dict[str, MethodBenchmarkResult]:
        """
        벤치마크 실행

        Args:
            test_cases: 테스트 케이스 리스트
            progress_interval: 진행률 표시 간격

        Returns:
            방법별 벤치마크 결과
        """
        self.results = {}

        for method_key, (tokenizer, detokenizer) in self.methods.items():
            print(f"\n[{self.method_names[method_key]}] 테스트 중...")

            result = MethodBenchmarkResult(method_name=self.method_names[method_key])
            start_time = time.time()

            for i, original in enumerate(test_cases):
                try:
                    # 자소 분리
                    tokens = tokenizer(original)

                    # 복원
                    restored = detokenizer(tokens)

                    # 검증
                    is_success = restored == original

                    # 레코드 생성
                    record = BenchmarkRecord(
                        index=i,
                        original=original,
                        tokens=tokens,
                        restored=restored,
                        is_success=is_success,
                        error_message=(
                            None
                            if is_success
                            else f"Expected: {original}, Got: {restored}"
                        ),
                    )

                    result.add_record(record)

                except Exception as e:
                    # 에러 발생 시
                    record = BenchmarkRecord(
                        index=i,
                        original=original,
                        tokens=[],
                        restored="",
                        is_success=False,
                        error_message=f"Exception: {str(e)}",
                    )
                    result.add_record(record)

                # 진행률 표시
                if progress_interval > 0 and (i + 1) % progress_interval == 0:
                    elapsed = time.time() - start_time
                    progress = (i + 1) / len(test_cases) * 100
                    print(
                        f"  진행: {i+1:,}/{len(test_cases):,} ({progress:.1f}%) - "
                        f"정답: {result.success_count:,}/{i+1:,} "
                        f"({result.success_count/(i+1)*100:.2f}%) - "
                        f"경과: {elapsed:.1f}초"
                    )

            result.total_time = time.time() - start_time
            self.results[method_key] = result

            # 결과 출력
            print(f"\n  완료")
            print(f"  정확도: {result.accuracy:.2f}%")
            print(f"  정답: {result.success_count:,}/{result.total_count:,}")
            print(f"  에러: {result.failure_count:,}개")
            print(f"  시간: {result.total_time:.1f}초")
            print(f"  처리량: {result.throughput:.1f} samples/s")

        return self.results

    def generate_markdown_report(
        self,
        test_cases: List[str],
        output_path: str,
        data_description: str = "테스트 데이터",
    ):
        """
        마크다운 리포트 생성

        Args:
            test_cases: 테스트 케이스 리스트
            output_path: 출력 파일 경로
            data_description: 데이터 설명
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# 한글 자소 복원 벤치마크 리포트

**생성 시간**: {timestamp}
**데이터**: {data_description}
**테스트 샘플 수**: {len(test_cases):,}개

---

## 1. 정확도 비교

| 순위 | 방식 | 정확도 | 정답/전체 | 에러 수 | 처리 시간 | 처리량 (samples/s) |
|------|------|--------|-----------|---------|-----------|-------------------|
"""

        # 정확도 순위
        acc_ranking = sorted(
            self.results.items(), key=lambda x: x[1].accuracy, reverse=True
        )

        for rank, (method_key, result) in enumerate(acc_ranking, 1):
            report += f"| {rank} | {result.method_name} | "
            report += f"{result.accuracy:.2f}% | "
            report += f"{result.success_count:,}/{result.total_count:,} | "
            report += f"{result.failure_count:,} | "
            report += f"{result.total_time:.1f}초 | "
            report += f"{result.throughput:.1f} |\n"

        report += "\n---\n\n## 2. 상세 분석\n\n"

        # 최고 성능 분석
        if "jaso_jamo" in self.results:
            jaso_jamo = self.results["jaso_jamo"]
            best_baseline_key = [k for k, _ in acc_ranking if k != "jaso_jamo"][0]
            best_baseline = self.results[best_baseline_key]
            improvement = jaso_jamo.accuracy - best_baseline.accuracyy

            report += f"### 2.1 정확도 개선\n\n"
            report += f"- **jaso_jamo 방식**: {jaso_jamo.accuracy:.2f}%\n"
            report += f"- **최고 기존 방식** ({best_baseline.method_name}): {best_baseline.accuracy:.2f}%\n"
            report += f"- **개선율**: {improvement:+.2f}%p\n"
            report += f"- **에러 감소**: {best_baseline.failure_count - jaso_jamo.failure_count:,}개\n\n"

            # jaso_jamo 방식 에러 케이스
            report += "### 2.2 jaso_jamo 방식 에러 케이스 (최대 20개)\n\n"

            if jaso_jamo.failure_count > 0:
                failures = jaso_jamo.get_failure_summary(max_count=20)
                report += "| # | 원본 (50자 제한) | 복원 결과 (50자 제한) |\n"
                report += "|---|-----------------|----------------------|\n"

                for i, failure in enumerate(failures, 1):
                    report += (
                        f"| {i} | {failure['original']} | {failure['restored']} |\n"
                    )

                if jaso_jamo.failure_count > 20:
                    report += f"\n... 외 {jaso_jamo.failure_count - 20:,}개 더 있음\n"
            else:
                report += "모든 테스트 케이스 통과\n"

        report += "\n---\n\n## 3. 테스트 데이터 샘플 (처음 20개)\n\n"
        report += "| # | 텍스트 (80자 제한) | 길이 |\n"
        report += "|---|-------------------|------|\n"

        for i, text in enumerate(test_cases[:20], 1):
            display = text[:80] + "..." if len(text) > 80 else text
            report += f"| {i} | {display} | {len(text)} |\n"

        if len(test_cases) > 20:
            report += f"\n... 외 {len(test_cases) - 20:,}개 더 있음\n"

        report += "\n---\n\n## 4. 결론\n\n"

        if "jaso_jamo" in self.results:
            jaso_jamo_result = self.results["jaso_jamo"]
            baseline_keys = [k for k in self.results.keys() if k != "jaso_jamo"]]

            if baseline_keys:
                best_baseline_result = max(
                    [self.results[k] for k in baseline_keys], key=lambda x: x.accuracy
                )
                improvement_value = (
                    jaso_jamo_result.accuracy - best_baseline_result.accuracy
                )

                if improvement_value > 5:
                    conclusion = "jaso_jamo 방식이 기존 방식 대비 압도적으로 우수합니다"
                elif improvement_value > 1:
                    conclusion = "jaso_jamo 방식이 기존 방식 대비 유의미하게 개선되었습니다"
                elif improvement_value > 0:
                    conclusion = "jaso_jamo 방식이 기존 방식 대비 소폭 개선되었습니다"
                else:
                    conclusion = "개선이 필요합니다"

                report += f"{conclusion}\n\n"
                report += f"- **테스트 규모**: {len(test_cases):,}개 샘플\n"
                report += f"- **데이터 유형**: {data_description}\n"
                report += f"- **정확도 개선**: {improvement_value:+.2f}%p\n"
                report += f"- **에러 감소**: {best_baseline_result.failure_count - jaso_jamo_result.failure_count:,}개\n"
            else:
                report += f"jaso_jamo 방식만 테스트됨\n\n"
                report += f"- **테스트 규모**: {len(test_cases):,}개 샘플\n"
                report += f"- **데이터 유형**: {data_description}\n"

        # 파일 저장
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n리포트 저장: {output_path}")

    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "=" * 80)
        print("벤치마크 결과 요약")
        print("=" * 80)

        for method_key, result in self.results.items():
            print(f"\n{result.method_name}")
            print(f"  정확도: {result.accuracy:.2f}%")
            print(f"  정답: {result.success_count:,}/{result.total_count:,}")
            print(f"  에러: {result.failure_count:,}개")
            print(f"  시간: {result.total_time:.1f}초")
            print(f"  처리량: {result.throughput:.1f} samples/s")

        print("\n" + "=" * 80)
        print("완료")
        print("=" * 80)

    def generate_error_report(self, output_path: str, max_samples: int = 3):
        """
        에러 케이스 상세 분석 리포트 생성

        Args:
            output_path: 출력 파일 경로
            max_samples: 방식별 최대 샘플 개수
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# 한글 자소 복원 에러 분석 리포트

**생성 시간**: {timestamp}

---

"""

        for method_key, result in self.results.items():
            if result.failure_count == 0:
                continue

            report += f"## {result.method_name}\n\n"
            report += f"- **전체**: {result.total_count:,}개\n"
            report += (
                f"- **성공**: {result.success_count:,}개 ({result.accuracy:.2f}%)\n"
            )
            report += f"- **실패**: {result.failure_count:,}개\n\n"
            report += f"### 에러 샘플 (최대 {max_samples}개)\n\n"

            failures = result.get_failure_summary(max_count=max_samples)

            for i, failure in enumerate(failures, 1):
                report += f"#### 샘플 {i}\n\n"
                report += f"**원본**:\n```\n{failure['original']}\n```\n\n"

                # 자모 분리 (tokenize)
                from jaso_jamo import tokenize

                tokens = tokenize(failure["original"])
                tokens_str = " ".join(tokens)
                report += f"**자모 분리**:\n```\n{tokens_str}\n```\n\n"

                report += f"**복원 결과**:\n```\n{failure['restored']}\n```\n\n"
                report += "---\n\n"

            if result.failure_count > max_samples:
                report += f"... 외 {result.failure_count - max_samples:,}개 더 있음\n\n"

        # 파일 저장
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n에러 리포트 저장: {output_path}")
