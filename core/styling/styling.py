from typing import NamedTuple, List

from core.styling.cssrule import CssRule


class Style(NamedTuple):
    selector: str
    rule: CssRule


def make_stylesheet(
        rules: List[Style],
        *,
        ident: int = 4,
        do_ident_closing_brace: bool = True
):
    lines = []

    for rule in rules:
        lines.append(f"{rule.selector} {{")
        for k, v in rule.rule.items():
            lines.append(f"{' ' * ident}{k}: {v};")

        lines.append(f"{' ' * ident * do_ident_closing_brace}}}")

    return "\n".join(lines)