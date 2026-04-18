"""Zet Blockly XML om naar Robot Framework code."""

import xml.etree.ElementTree as ET


# Koppelt een bloktype aan een Robot keyword en de velden die nodig zijn.
BLOCK_MAP = {
    "open_browser": ("Open Browser", ["URL", "BROWSER"]),
    "maximize_window": ("Maximize Browser Window", []),
    "wait_seconds": ("Sleep", ["SECONDS"]),
    "assert_title": ("Title Should Be", ["EXPECTED_TITLE"]),
    "close_browser": ("Close Browser", []),
}

def local_tag(element: ET.Element) -> str:
    """
    Geeft de tagnaam terug zonder XML namespace.

    Args:
        element (ET.Element): XML element waarvan de tag nodig is.

    Returns:
        str: Tagnaam zonder namespace.
    """
    return element.tag.split("}")[-1]


def find_child(element: ET.Element, tag_name: str) -> ET.Element | None:
    """
    Zoekt een direct child element op tagnaam.

    Args:
        element (ET.Element): Het parent XML element.
        tag_name (str): De gezochte tagnaam.

    Returns:
        ET.Element | None: Het gevonden child element of None.
    """
    for child in element:
        if local_tag(child) == tag_name:
            return child
    return None


def find_children(element: ET.Element, tag_name: str) -> list[ET.Element]:
    """
    Zoekt alle directe child elementen op tagnaam.

    Args:
        element (ET.Element): Het parent XML element.
        tag_name (str): De gezochte tagnaam.

    Returns:
        list[ET.Element]: Lijst met gevonden child elementen.
    """
    return [child for child in element if local_tag(child) == tag_name]


def get_field(block: ET.Element, field_name: str) -> str:
    """
    Haalt de waarde van een veld uit een blok.

    Args:
        block (ET.Element): Het Blockly blok.
        field_name (str): Naam van het veld.

    Returns:
        str: De veldwaarde of een lege string.
    """
    for field in find_children(block, "field"):
        if field.get("name") == field_name and field.text:
            return field.text.strip()
    return ""


def block_to_robot(block: ET.Element) -> str | None:
    """
    Zet één blok om naar één Robot regel.

    Args:
        block (ET.Element): Het Blockly blok.

    Returns:
        str | None: De Robot regel of None bij een onbekend blok.
    """
    block_type = block.get("type")

    if block_type not in BLOCK_MAP:
        # Onbekende blokken slaan we over.
        return None

    keyword, fields = BLOCK_MAP[block_type]
    args = [get_field(block, field_name) for field_name in fields]

    # Sleep moet altijd eindigen op seconden.
    if block_type == "wait_seconds" and args and not args[0].endswith("s"):
        args[0] += "s"

    # Maak van keyword en velden één regel.
    parts = [keyword] + args
    return "    " + "    ".join(parts)


def parse_blocks(root: ET.Element) -> list[str]:
    """
    Leest alle blokken in de workspace en zet ze om naar Robot regels.

    Args:
        root (ET.Element): Het root XML element.

    Returns:
        list[str]: Lijst met Robot regels.
    """
    code_lines = []

    for top_block in find_children(root, "block"):
        # Loop door de hele blokketen via <next>.
        current = top_block
        while current is not None:
            line = block_to_robot(current)
            if line:
                code_lines.append(line)

            # Pak het volgende blok uit de keten.
            next_element = find_child(current, "next")
            current = find_child(next_element, "block") if next_element is not None else None

    return code_lines


def xml_to_robot(xml_text: str) -> tuple[str, str]:
    """
    Converteert Blockly XML naar Robot Framework code.

    Args:
        xml_text (str): De Blockly workspace als XML string.

    Returns:
        tuple[str, str]: Preview code en volledig Robot bestand.

    Raises:
        ValueError: Als de XML niet geldig is.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as error:
        raise ValueError(f"Ongeldige XML: {error}")

    # Maak eerst de losse regels voor de teststappen.
    code_lines = parse_blocks(root)
    keywords_code = "\n".join(code_lines)

    # Bouw daarna het volledige Robot bestand op.
    robot_file = (
        "*** Settings ***\n"
        "Library    SeleniumLibrary\n"
        "\n"
        "*** Test Cases ***\n"
        "Generated Test\n"
        f"{keywords_code}\n"
    )

    return keywords_code, robot_file
