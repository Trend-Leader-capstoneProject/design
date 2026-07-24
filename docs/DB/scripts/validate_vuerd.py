from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"파일을 찾을 수 없습니다: {file_path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"유효하지 않은 JSON입니다: line={exc.lineno}, column={exc.colno}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("JSON 최상위 값은 객체여야 합니다.")

    return data


def find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)

    return sorted(duplicates)


def validate_vuerd(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    doc = data.get("doc")
    collections = data.get("collections")

    if not isinstance(doc, dict):
        return ["doc 객체가 존재하지 않습니다."], warnings

    if not isinstance(collections, dict):
        return ["collections 객체가 존재하지 않습니다."], warnings

    table_entities = collections.get("tableEntities", {})
    column_entities = collections.get("tableColumnEntities", {})
    relationship_entities = collections.get("relationshipEntities", {})
    index_entities = collections.get("indexEntities", {})

    if not isinstance(table_entities, dict):
        errors.append("collections.tableEntities가 객체가 아닙니다.")
        table_entities = {}

    if not isinstance(column_entities, dict):
        errors.append("collections.tableColumnEntities가 객체가 아닙니다.")
        column_entities = {}

    if not isinstance(relationship_entities, dict):
        errors.append("collections.relationshipEntities가 객체가 아닙니다.")
        relationship_entities = {}

    if not isinstance(index_entities, dict):
        errors.append("collections.indexEntities가 객체가 아닙니다.")
        index_entities = {}

    active_table_ids = doc.get("tableIds", [])
    active_relationship_ids = doc.get("relationshipIds", [])
    active_index_ids = doc.get("indexIds", [])

    if not isinstance(active_table_ids, list):
        errors.append("doc.tableIds가 배열이 아닙니다.")
        active_table_ids = []

    if not isinstance(active_relationship_ids, list):
        errors.append("doc.relationshipIds가 배열이 아닙니다.")
        active_relationship_ids = []

    if not isinstance(active_index_ids, list):
        errors.append("doc.indexIds가 배열이 아닙니다.")
        active_index_ids = []

    active_table_ids = [str(value) for value in active_table_ids]
    active_relationship_ids = [str(value) for value in active_relationship_ids]
    active_index_ids = [str(value) for value in active_index_ids]

    duplicate_table_ids = find_duplicates(active_table_ids)
    if duplicate_table_ids:
        errors.append(
            "doc.tableIds에 중복 ID가 있습니다: "
            + ", ".join(duplicate_table_ids)
        )

    active_table_id_set = set(active_table_ids)
    table_entity_id_set = set(table_entities)

    missing_tables = active_table_id_set - table_entity_id_set
    if missing_tables:
        errors.append(
            "doc.tableIds에는 있지만 tableEntities에 없는 테이블: "
            + ", ".join(sorted(missing_tables))
        )

    inactive_tables = table_entity_id_set - active_table_id_set
    if inactive_tables:
        errors.append(
            "doc.tableIds에 포함되지 않은 잔여 테이블 엔티티: "
            + ", ".join(sorted(inactive_tables))
        )

    referenced_column_ids: set[str] = set()

    for table_id in active_table_ids:
        table = table_entities.get(table_id)
        if not isinstance(table, dict):
            continue

        table_name = str(table.get("name", "")).strip()

        if not table_name:
            errors.append(f"이름이 비어 있는 테이블: {table_id}")

        column_ids = table.get("columnIds", [])
        sequence_column_ids = table.get("seqColumnIds", [])

        if not isinstance(column_ids, list):
            errors.append(f"{table_name or table_id}.columnIds가 배열이 아닙니다.")
            column_ids = []

        if not isinstance(sequence_column_ids, list):
            errors.append(
                f"{table_name or table_id}.seqColumnIds가 배열이 아닙니다."
            )
            sequence_column_ids = []

        column_ids = [str(value) for value in column_ids]
        sequence_column_ids = [str(value) for value in sequence_column_ids]

        duplicate_column_ids = find_duplicates(column_ids)
        if duplicate_column_ids:
            errors.append(
                f"{table_name or table_id}.columnIds 중복: "
                + ", ".join(duplicate_column_ids)
            )

        duplicate_sequence_ids = find_duplicates(sequence_column_ids)
        if duplicate_sequence_ids:
            errors.append(
                f"{table_name or table_id}.seqColumnIds 중복: "
                + ", ".join(duplicate_sequence_ids)
            )

        column_id_set = set(column_ids)
        sequence_column_id_set = set(sequence_column_ids)

        sequence_only = sequence_column_id_set - column_id_set
        if sequence_only:
            errors.append(
                f"{table_name or table_id}.seqColumnIds에만 존재하는 컬럼: "
                + ", ".join(sorted(sequence_only))
            )

        column_only = column_id_set - sequence_column_id_set
        if column_only:
            errors.append(
                f"{table_name or table_id}.columnIds에만 존재하는 컬럼: "
                + ", ".join(sorted(column_only))
            )

        for column_id in column_ids:
            referenced_column_ids.add(column_id)

            column = column_entities.get(column_id)
            if not isinstance(column, dict):
                errors.append(
                    f"{table_name or table_id}가 존재하지 않는 컬럼을 참조합니다: "
                    f"{column_id}"
                )
                continue

            column_name = str(column.get("name", "")).strip()
            data_type = str(column.get("dataType", "")).strip()
            owner_table_id = str(column.get("tableId", ""))

            if not column_name:
                errors.append(
                    f"{table_name or table_id}에 이름이 비어 있는 컬럼이 있습니다: "
                    f"{column_id}"
                )

            if not data_type:
                errors.append(
                    f"{table_name or table_id}.{column_name or column_id}의 "
                    "dataType이 비어 있습니다."
                )

            if owner_table_id != table_id:
                errors.append(
                    f"컬럼 {column_id}의 tableId가 실제 소유 테이블과 다릅니다: "
                    f"expected={table_id}, actual={owner_table_id}"
                )

    orphan_column_ids = set(column_entities) - referenced_column_ids
    if orphan_column_ids:
        errors.append(
            "활성 테이블의 columnIds에서 참조되지 않는 잔여 컬럼 엔티티: "
            + ", ".join(sorted(orphan_column_ids))
        )

    active_relationship_id_set = set(active_relationship_ids)
    relationship_entity_id_set = set(relationship_entities)

    missing_relationships = (
        active_relationship_id_set - relationship_entity_id_set
    )
    if missing_relationships:
        errors.append(
            "doc.relationshipIds에는 있지만 relationshipEntities에 없는 관계: "
            + ", ".join(sorted(missing_relationships))
        )

    inactive_relationships = (
        relationship_entity_id_set - active_relationship_id_set
    )
    if inactive_relationships:
        errors.append(
            "doc.relationshipIds에 포함되지 않은 잔여 관계 엔티티: "
            + ", ".join(sorted(inactive_relationships))
        )

    for relationship_id in active_relationship_ids:
        relationship = relationship_entities.get(relationship_id)
        if not isinstance(relationship, dict):
            continue

        for endpoint_name in ("start", "end"):
            endpoint = relationship.get(endpoint_name)

            if not isinstance(endpoint, dict):
                errors.append(
                    f"관계 {relationship_id}의 {endpoint_name}가 없습니다."
                )
                continue

            table_id = str(endpoint.get("tableId", ""))
            column_ids = endpoint.get("columnIds", [])

            if table_id not in active_table_id_set:
                errors.append(
                    f"관계 {relationship_id}가 존재하지 않는 테이블을 참조합니다: "
                    f"{table_id}"
                )

            if not isinstance(column_ids, list):
                errors.append(
                    f"관계 {relationship_id}.{endpoint_name}.columnIds가 "
                    "배열이 아닙니다."
                )
                continue

            for column_id_value in column_ids:
                column_id = str(column_id_value)
                column = column_entities.get(column_id)

                if not isinstance(column, dict):
                    errors.append(
                        f"관계 {relationship_id}가 존재하지 않는 컬럼을 "
                        f"참조합니다: {column_id}"
                    )
                    continue

                owner_table_id = str(column.get("tableId", ""))
                if owner_table_id != table_id:
                    errors.append(
                        f"관계 {relationship_id}의 컬럼 소유 테이블이 "
                        f"일치하지 않습니다: column={column_id}, "
                        f"endpoint_table={table_id}, owner_table={owner_table_id}"
                    )

    active_index_id_set = set(active_index_ids)
    index_entity_id_set = set(index_entities)

    missing_indexes = active_index_id_set - index_entity_id_set
    if missing_indexes:
        errors.append(
            "doc.indexIds에는 있지만 indexEntities에 없는 인덱스: "
            + ", ".join(sorted(missing_indexes))
        )

    inactive_indexes = index_entity_id_set - active_index_id_set
    if inactive_indexes:
        errors.append(
            "doc.indexIds에 포함되지 않은 잔여 인덱스 엔티티: "
            + ", ".join(sorted(inactive_indexes))
        )

    if not active_index_ids:
        warnings.append(
            "인덱스가 아직 정의되지 않았습니다. "
            "UNIQUE 및 조회 인덱스 설계 단계에서 추가해야 합니다."
        )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ERD Editor vuerd.json 구조를 검증합니다."
    )
    parser.add_argument(
        "file",
        type=Path,
        help="검증할 .vuerd.json 파일 경로",
    )
    args = parser.parse_args()

    try:
        data = load_json(args.file)
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 1

    errors, warnings = validate_vuerd(data)

    for warning in warnings:
        print(f"[WARN] {warning}")

    if errors:
        print(f"[FAIL] 총 {len(errors)}개의 오류를 발견했습니다.")
        for index, error in enumerate(errors, start=1):
            print(f"  {index}. {error}")
        return 1

    print("[PASS] ERD JSON 구조 검증을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())