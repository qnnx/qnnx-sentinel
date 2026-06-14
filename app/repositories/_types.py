from uuid import UUID


def as_uuid(value):
    if value is None or isinstance(value, UUID):
        return value
    return UUID(str(value))


def normalize_uuid_fields(data: dict, *field_names: str) -> dict:
    normalized = dict(data)
    for field_name in field_names:
        if normalized.get(field_name) is not None:
            normalized[field_name] = as_uuid(normalized[field_name])
    return normalized
