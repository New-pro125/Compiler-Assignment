from typing import List, Optional, Tuple


def ranges_overlap(r1: Tuple[str, str], r2: Tuple[str, str]) -> bool:
    return r1[0] <= r2[1] and r2[0] <= r1[1]


def ranges_adjacent(r1: Tuple[str, str], r2: Tuple[str, str]) -> bool:
    if r1[0] == r1[1] and r2[0] == r2[1]:  # Ranges are just a characters
        return False
    return ord(r1[1]) + 1 == ord(r2[0]) or ord(r2[1]) + 1 == ord(r1[0])


def is_class_token(token: str) -> bool:
    return token.startswith("[") and token.endswith("]")


def is_character_token(token: str) -> bool:
    return token != "." and not is_class_token(token) and len(token) == 1


def parse_ranges(token: str) -> List[Tuple[str, str]]:
    inner: str = token[1:-1]
    ranges: List[Tuple[str, str]] = []
    i: int = 0
    while i < len(inner):
        if i + 2 < len(inner) and inner[i + 1] == "-":
            ranges.append((inner[i], inner[i + 2]))
            i += 3
        else:
            ranges.append((inner[i], inner[i]))
            i += 1
    return ranges


def is_char_inside_range(char: str, token: str) -> bool:
    if token == ".":
        return True
    if not is_class_token(token) or len(char) != 1:
        return False
    for low, high in parse_ranges(token):
        if low <= char <= high:
            return True
    return False


def is_range_inside_range(sub_token: str, sup_token: str) -> bool:
    if sup_token == ".":
        return True
    if (
        sub_token == "."
        or not is_class_token(sub_token)
        or not is_class_token(sup_token)
    ):
        return False
    sub_ranges: List[Tuple[str, str]] = parse_ranges(sub_token)
    sup_ranges: List[Tuple[str, str]] = parse_ranges(sup_token)

    return all(
        any(
            wide_low <= narrow_low and narrow_high <= wide_high
            for wide_low, wide_high in sup_ranges
        )
        for narrow_low, narrow_high in sub_ranges
    )


def symbol_is_subsumed(specific: str, general: str) -> bool:
    if specific == general:
        return True
    if general == ".":
        return True
    if specific == ".":
        return False
    if is_character_token(specific) and is_class_token(general):
        return is_char_inside_range(specific, general)
    if is_class_token(specific) and is_class_token(general):
        return is_range_inside_range(specific, general)
    return False


def _symbol_to_ranges(token: str) -> Optional[List[Tuple[str, str]]]:
    if token == ".":
        return None
    if is_class_token(token):
        return parse_ranges(token)
    if is_character_token(token):
        return [(token, token)]
    return None


def _build_class_token(ranges: List[Tuple[str, str]]) -> str:
    parts: List[str] = [f"{low}-{high}" if low != high else low for low, high in ranges]
    return "[" + "".join(parts) + "]"


def merge_overlapping_ranges(token_a: str, token_b: str) -> Optional[str]:
    if token_a == "." or token_b == ".":
        return "."

    ranges_a = _symbol_to_ranges(token_a)
    ranges_b = _symbol_to_ranges(token_b)
    if ranges_a is None or ranges_b is None:
        return None

    all_ranges: List[Tuple[str, str]] = sorted(
        ranges_a + ranges_b, key=lambda item: item[0]
    )

    has_overlap: bool = any(
        ranges_overlap(all_ranges[i], all_ranges[i + 1])
        or ranges_adjacent(all_ranges[i], all_ranges[i + 1])
        for i in range(len(all_ranges) - 1)
    )
    if not has_overlap:
        return None

    merged: List[Tuple[str, str]] = [all_ranges[0]]
    for low, high in all_ranges[1:]:
        prev_low, prev_high = merged[-1]
        previous: Tuple[str, str] = (prev_low, prev_high)
        current: Tuple[str, str] = (low, high)
        if ranges_overlap(previous, current) or ranges_adjacent(previous, current):
            merged[-1] = (prev_low, max(prev_high, high))
            continue
        merged.append(current)

    return _build_class_token(merged)
