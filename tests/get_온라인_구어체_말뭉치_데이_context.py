"""
AI Hub 온라인 구어체 말뭉치 데이터에서 content 추출
D:\\temp\\031.온라인_구어체_말뭉치_데이터\\01.데이터\\1.Training_220728_add\\원천데이터\\TS1
"""

import json
import sys
import io
from pathlib import Path

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def extract_contents_from_json(json_path: Path) -> list:
    """
    JSON 파일에서 모든 content 추출

    Args:
        json_path: JSON 파일 경로

    Returns:
        content 리스트
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # SJML.text[] 구조에서 content 추출
        contents = []
        if 'SJML' in data and 'text' in data['SJML']:
            for item in data['SJML']['text']:
                if 'content' in item and item['content'].strip():
                    contents.append(item['content'].strip())

        return contents

    except Exception as e:
        print(f"Error ({json_path.name}): {e}")
        return []


def main():
    """메인 함수"""
    # 경로 설정
    ROOT_DIR = r"D:\temp\031.온라인_구어체_말뭉치_데이터\01.데이터\1.Training_220728_add\원천데이터\TS1"
    OUTPUT_FILE = r"d:\GoogleDrive\homepage\hangul_jaso\.data\온라인_구어체_말뭉치_데이_context.txt"

    root_path = Path(ROOT_DIR)

    if not root_path.exists():
        print(f"경로가 존재하지 않습니다: {ROOT_DIR}")
        return

    print("=" * 80)
    print("AI Hub 온라인 구어체 말뭉치 Content 추출")
    print("=" * 80)
    print(f"루트 경로: {ROOT_DIR}")
    print(f"출력 파일: {OUTPUT_FILE}\n")

    # 모든 JSON 파일 찾기
    json_files = list(root_path.rglob("*.json"))
    total_files = len(json_files)

    print(f"발견된 JSON 파일: {total_files:,}개\n")

    if total_files == 0:
        print("JSON 파일을 찾을 수 없습니다.")
        return

    # Content 추출
    all_contents = []
    processed = 0

    print("처리 중...\n")

    for i, json_file in enumerate(json_files, 1):
        # 진행률 표시
        if i % 100 == 0 or i == total_files:
            progress = i / total_files * 100
            print(f"  진행: {i:,}/{total_files:,} ({progress:.1f}%) - 추출: {len(all_contents):,}개")

        contents = extract_contents_from_json(json_file)

        if contents:
            processed += 1
            all_contents.extend(contents)

    print(f"\n처리 완료!\n")

    # 통계
    print("=" * 80)
    print("추출 통계")
    print("=" * 80)
    print(f"총 JSON 파일: {total_files:,}개")
    print(f"처리 성공: {processed:,}개")
    print(f"추출된 content: {len(all_contents):,}개\n")

    # 파일 저장
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("파일 저장 중...\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        for content in all_contents:
            f.write(content + '\n')

    print(f"저장 완료: {OUTPUT_FILE}")
    print(f"저장된 라인 수: {len(all_contents):,}개\n")

    # 샘플 출력
    print("=" * 80)
    print("샘플 데이터 (처음 10개)")
    print("=" * 80)

    for i, content in enumerate(all_contents[:10], 1):
        display = content[:80] + "..." if len(content) > 80 else content
        print(f"{i:2d}. {display}")

    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
