
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def cleanup_erd(data: dict[str, Any]) -> dict[str, int]:
    doc = data["doc"]
    collections = data["collections"]

    tables: dict[str, dict[str, Any]] = collections["tableEntities"]
    columns: dict[str, dict[str, Any]] = collections["tableColumnEntities"]
    relationships: dict[str, dict[str, Any]] = collections["relationshipEntities"]

    original_table_count = len(tables)
    original_column_count = len(columns)
    original_relationship_count = len(relationships)

    # doc.tableIds를 현재 화면에 존재하는 테이블의 기준으로 사용합니다.
    active_table_ids = [
        table_id
        for table_id in doc.get("tableIds", [])
        if table_id in tables
    ]
    active_table_id_set = set(active_table_ids)
    doc["tableIds"] = active_table_ids

    # 활성 테이블만 남기고, 각 테이블의 columnIds/seqColumnIds를 정리합니다.
    cleaned_tables: dict[str, dict[str, Any]] = {}
    active_column_ids: set[str] = set()

    for table_id in active_table_ids:
        table = tables[table_id]

        column_ids = [
            column_id
            for column_id in table.get("columnIds", [])
            if column_id in columns
            and columns[column_id].get("tableId") == table_id
        ]
        column_id_set = set(column_ids)

        # seqColumnIds에 남은 삭제 컬럼을 제거하고,
        # columnIds에는 있지만 seqColumnIds에서 빠진 컬럼은 뒤에 보충합니다.
        seq_column_ids = [
            column_id
            for column_id in table.get("seqColumnIds", [])
            if column_id in column_id_set
        ]
        seq_column_id_set = set(seq_column_ids)
        seq_column_ids.extend(
            column_id
            for column_id in column_ids
            if column_id not in seq_column_id_set
        )

        table["columnIds"] = column_ids
        table["seqColumnIds"] = seq_column_ids

        active_column_ids.update(column_ids)
        cleaned_tables[table_id] = table

    collections["tableEntities"] = cleaned_tables

    # 어느 활성 테이블에서도 참조하지 않는 컬럼 객체를 제거합니다.
    collections["tableColumnEntities"] = {
        column_id: column
        for column_id, column in columns.items()
        if column_id in active_column_ids
    }

    # doc.relationshipIds에 등록되어 있고,
    # 활성 테이블/컬럼만 참조하는 관계만 유지합니다.
    cleaned_relationship_ids: list[str] = []
    cleaned_relationships: dict[str, dict[str, Any]] = {}

    for relationship_id in doc.get("relationshipIds", []):
        relationship = relationships.get(relationship_id)
        if relationship is None:
            continue

        start = relationship.get("start", {})
        end = relationship.get("end", {})

        start_table_id = start.get("tableId")
        end_table_id = end.get("tableId")
        start_column_ids = start.get("columnIds", [])
        end_column_ids = end.get("columnIds", [])

        tables_are_valid = (
            start_table_id in active_table_id_set
            and end_table_id in active_table_id_set
        )
        columns_are_valid = (
            all(column_id in active_column_ids for column_id in start_column_ids)
            and all(column_id in active_column_ids for column_id in end_column_ids)
        )

        if not tables_are_valid or not columns_are_valid:
            continue

        cleaned_relationship_ids.append(relationship_id)
        cleaned_relationships[relationship_id] = relationship

    doc["relationshipIds"] = cleaned_relationship_ids
    collections["relationshipEntities"] = cleaned_relationships

    return {
        "removed_tables": original_table_count - len(cleaned_tables),
        "removed_columns": original_column_count
        - len(collections["tableColumnEntities"]),
        "removed_relationships": original_relationship_count
        - len(cleaned_relationships),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ERD Editor JSON의 삭제 후 잔여 객체를 정리합니다."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="정리할 .erd.json 또는 .vuerd.json 파일",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="원본 파일을 직접 수정하고 .bak 백업을 생성합니다.",
    )
    args = parser.parse_args()

    input_path: Path = args.input.resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    data = load_json(input_path)
    result = cleanup_erd(data)

    if args.in_place:
        backup_path = input_path.with_suffix(input_path.suffix + ".bak")
        shutil.copy2(input_path, backup_path)
        output_path = input_path
    else:
        output_path = input_path.with_name(
            f"{input_path.stem}.cleaned{input_path.suffix}"
        )

    save_json(output_path, data)

    print(f"출력 파일: {output_path}")
    print(f"제거된 테이블 객체: {result['removed_tables']}개")
    print(f"제거된 컬럼 객체: {result['removed_columns']}개")
    print(f"제거된 관계 객체: {result['removed_relationships']}개")


if __name__ == "__main__":
    main()
