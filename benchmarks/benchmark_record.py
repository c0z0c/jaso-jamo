"""
벤치마크 레코드 클래스
각 테스트의 원본, 자모, 복원 결과, 성공 여부, 실패 정보를 메모리에 저장
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BenchmarkRecord:
    """단일 테스트 케이스의 벤치마크 레코드"""
    
    index: int
    original: str
    tokens: List[str]
    restored: str
    is_success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'index': self.index,
            'original': self.original,
            'tokens': self.tokens,
            'restored': self.restored,
            'is_success': self.is_success,
            'error_message': self.error_message
        }


@dataclass
class MethodBenchmarkResult:
    """특정 방법의 전체 벤치마크 결과"""
    
    method_name: str
    records: List[BenchmarkRecord] = field(default_factory=list)
    total_time: float = 0.0
    
    @property
    def total_count(self) -> int:
        """전체 테스트 개수"""
        return len(self.records)
    
    @property
    def success_count(self) -> int:
        """성공 개수"""
        return sum(1 for r in self.records if r.is_success)
    
    @property
    def failure_count(self) -> int:
        """실패 개수"""
        return self.total_count - self.success_count
    
    @property
    def accuracy(self) -> float:
        """정확도 (%)"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100
    
    @property
    def failures(self) -> List[BenchmarkRecord]:
        """실패한 레코드 목록"""
        return [r for r in self.records if not r.is_success]
    
    @property
    def throughput(self) -> float:
        """처리량 (samples/s)"""
        if self.total_time == 0:
            return 0.0
        return self.total_count / self.total_time
    
    def add_record(self, record: BenchmarkRecord):
        """레코드 추가"""
        self.records.append(record)
    
    def get_failure_summary(self, max_count: int = 20) -> List[dict]:
        """실패 케이스 요약 (최대 개수 제한)"""
        failures = self.failures[:max_count]
        return [
            {
                'index': f.index,
                'original': f.original[:50] + '...' if len(f.original) > 50 else f.original,
                'restored': f.restored[:50] + '...' if len(f.restored) > 50 else f.restored,
                'error': f.error_message
            }
            for f in failures
        ]
