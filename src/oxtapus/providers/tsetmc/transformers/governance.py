"""Pure corporate-governance disclosure transformations."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

import polars as pl
from pydantic import ValidationError

from oxtapus.domain.calendar import EXCHANGE_TIMEZONE
from oxtapus.domain.errors import SchemaValidationError
from oxtapus.domain.governance import BOARD_MEMBER_COLUMNS
from oxtapus.domain.identifiers import normalize_persian
from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.queries import BoardMembersQuery
from oxtapus.providers.tsetmc.source_models import BoardStatementSource

_KNOWN_XML_TAGS = {
    "Agent",
    "AgentNationalCode",
    "AssemblyDate",
    "BoardMember",
    "BoardMembers",
    "BoardMembersSessionDate",
    "Charged",
    "Designation",
    "DirectorManager",
    "DirectorManagerEducationDegree",
    "DirectorManagerName",
    "DirectorManagerNationalCode",
    "EducationDegree",
    "MemberName",
    "NationalCode_RegisterNumber",
    "PreviousMemberName",
    "PreviuosAgent",
    "Root",
}


def transform_board_members(
    records: list[dict[str, object]], query: BoardMembersQuery
) -> TransformOutput:
    """Flatten board-member XML statements into one canonical row per member."""

    try:
        statements = [BoardStatementSource.model_validate(record) for record in records]
    except ValidationError as exc:
        raise SchemaValidationError("Board statements violate their source contract.") from exc
    rows: list[dict[str, object]] = []
    unknown_xml_tags: set[str] = set()
    for statement in statements:
        root = _parse_xml(statement.content)
        unknown_xml_tags.update(
            f"content.{element.tag}"
            for element in root.iter()
            if element.tag not in _KNOWN_XML_TAGS
        )
        members = root.findall("./BoardMembers/BoardMember")
        chief_executive = root.find("./DirectorManager")
        shared = {
            "tsetmc_instrument_code": query.tsetmc_instrument_code,
            "symbol": query.symbol,
            "statement_title": normalize_persian(statement.title),
            "sent_at": _parse_source_datetime(statement.sentDateTime_Gregorian),
            "published_at": _parse_source_datetime(statement.publishDateTime_Gregorian),
            "publication_date": _parse_yyyymmdd(statement.publishDateTime_DEven),
            "report_subtype": statement.reportSubType,
            "page_id": statement.pageID,
            "is_correction": "اصلاحیه" in statement.title,
            "assembly_date_jalali": _text(root, "AssemblyDate"),
            "board_session_date_jalali": _text(root, "BoardMembersSessionDate"),
            "chief_executive_name": _text(chief_executive, "DirectorManagerName"),
            "chief_executive_national_code": _plain_text(
                chief_executive, "DirectorManagerNationalCode"
            ),
            "chief_executive_education_degree": _text(
                chief_executive, "DirectorManagerEducationDegree"
            ),
        }
        if not members:
            rows.append(_member_row(shared, None))
            continue
        rows.extend(_member_row(shared, member) for member in members)
    frame = (
        pl.DataFrame(rows, schema=_schema()).select(BOARD_MEMBER_COLUMNS)
        if rows
        else pl.DataFrame(schema=_schema()).select(BOARD_MEMBER_COLUMNS)
    )
    if frame.height:
        frame = frame.sort(["published_at", "member_name"], descending=[True, False])
    unknown = {
        field for statement in statements for field in statement.unknown_fields()
    } | unknown_xml_tags
    return TransformOutput(data=frame, unknown_fields=tuple(sorted(unknown)))


def _member_row(
    shared: Mapping[str, object], member: ElementTree.Element | None
) -> dict[str, object]:
    return {
        **shared,
        "member_name": _text(member, "MemberName"),
        "national_code_or_registration_number": _plain_text(member, "NationalCode_RegisterNumber"),
        "designation": _text(member, "Designation"),
        "duty_status": _text(member, "Charged"),
        "education_degree": _text(member, "EducationDegree"),
        "agent_name": _text(member, "Agent"),
        "agent_national_code": _plain_text(member, "AgentNationalCode"),
        "previous_member_name": _text(member, "PreviousMemberName"),
        "previous_agent_name": _text(member, "PreviuosAgent"),
    }


def _parse_xml(content: str) -> ElementTree.Element:
    if "<!DOCTYPE" in content.upper() or "<!ENTITY" in content.upper():
        raise SchemaValidationError("Board statement XML declarations are not allowed.")
    try:
        return ElementTree.fromstring(content)
    except ElementTree.ParseError as exc:
        raise SchemaValidationError("Board statement content is malformed XML.") from exc


def _parse_source_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise SchemaValidationError("Board statement datetime is malformed.") from exc
    return parsed.replace(tzinfo=ZoneInfo(EXCHANGE_TIMEZONE)) if parsed.tzinfo is None else parsed


def _parse_yyyymmdd(value: int) -> date:
    text = str(value)
    try:
        return date.fromisoformat(f"{text[:4]}-{text[4:6]}-{text[6:]}")
    except ValueError as exc:
        raise SchemaValidationError("Board statement publication date is malformed.") from exc


def _plain_text(parent: ElementTree.Element | None, path: str) -> str | None:
    if parent is None:
        return None
    value = parent.findtext(path)
    if value is None:
        return None
    result = value.strip()
    return result or None


def _text(parent: ElementTree.Element | None, path: str) -> str | None:
    value = _plain_text(parent, path)
    return normalize_persian(value) if value else None


def _schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String(),
            "symbol": pl.String(),
            "statement_title": pl.String(),
            "sent_at": pl.Datetime(time_zone=EXCHANGE_TIMEZONE),
            "published_at": pl.Datetime(time_zone=EXCHANGE_TIMEZONE),
            "publication_date": pl.Date(),
            "report_subtype": pl.Int64(),
            "page_id": pl.Int64(),
            "is_correction": pl.Boolean(),
            "assembly_date_jalali": pl.String(),
            "board_session_date_jalali": pl.String(),
            "member_name": pl.String(),
            "national_code_or_registration_number": pl.String(),
            "designation": pl.String(),
            "duty_status": pl.String(),
            "education_degree": pl.String(),
            "agent_name": pl.String(),
            "agent_national_code": pl.String(),
            "previous_member_name": pl.String(),
            "previous_agent_name": pl.String(),
            "chief_executive_name": pl.String(),
            "chief_executive_national_code": pl.String(),
            "chief_executive_education_degree": pl.String(),
        }
    )
