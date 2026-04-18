"""
code_generator.py
Doel: converteert Blockly XML naar Robot Framework syntax zodat tests kunnen worden gerund.
"""
import xml.etree.ElementTree as ET


# Mapping: block_type
BLOCK_MAP = {
    'open_browser':      ('Open Browser',            ['URL', 'BROWSER']),
    'maximize_window':   ('Maximize Browser Window', []),
    'wait_seconds':      ('Sleep',                   ['SECONDS']),
    'assert_title':      ('Title Should Be',         ['EXPECTED_TITLE']),
    'close_browser':     ('Close Browser',           []),
}

# Standaard waarden per veld
FIELD_DEFAULTS = {
    'URL':            'https://example.com',
    'BROWSER':        'chrome',
    'SECONDS':        '1s',
    'EXPECTED_TITLE': 'Page Title',
}


def find_child(element: ET.Element, tag_name: str) -> ET.Element | None:
    """Zoekt een direct child element op tagnaam, ongeacht XML namespace."""
    for child in element:
        if child.tag.split('}')[-1] == tag_name:
            return child
    return None


def find_children(element: ET.Element, tag_name: str) -> list[ET.Element]:
    """Zoekt directe child elementen op tagnaam, ongeacht XML namespace."""
    return [child for child in element if child.tag.split('}')[-1] == tag_name]


def get_field(block: ET.Element, field_name: str) -> str:
    """
    Haalt de tekstwaarde op van een <field> element binnen een blok.
    
    Args:
        block (Element): het <block> element uit de XML
        field_name (str): naam van het veld (bijv. 'URL', 'SECONDS')
    
    Returns:
        str: de tekstwaarde, of standaardwaarde als niet gevonden
    """
    for field in find_children(block, 'field'):
        if field.get('name') == field_name and field.text:
            return field.text.strip()
    return FIELD_DEFAULTS.get(field_name, '')


def block_to_robot(block: ET.Element) -> str | None:
    """
    Zet één blok om naar een Robot Framework keyword regel.
    
    Args:
        block (Element): één <block> element uit het XML
    
    Returns:
        str: Robot Framework code regel, of None als bloktype onbekend is
    """
    block_type = block.get('type')
    
    if block_type not in BLOCK_MAP:
        return None  # Onbekend bloktype - overslaan
    
    keyword, fields = BLOCK_MAP[block_type]
    args = [get_field(block, f) for f in fields]
    
    # Speciaal geval: Sleep keyword heeft 's' suffix nodig (bijv. "5s")
    if block_type == 'wait_seconds' and args and not args[0].endswith('s'):
        args[0] += 's'
    
    # Bouw de Robot keyword regel op
    parts = [keyword] + args
    return '    ' + '    '.join(parts)


def parse_blocks(root: ET.Element) -> list[str]:
    """
    Gaat alle blokken langs (inclusief ketens via <next>) en zet ze om naar Robot code.
    
    Args:
        root (Element): het root XML element (van ET.fromstring())
    
    Returns:
        list[str]: lijst met Robot Framework code regels
    """
    code_lines = []
    
    for top_block in find_children(root, 'block'):
        # Walk de keten van blokken (via <next><block>...)
        current = top_block
        while current is not None:
            line = block_to_robot(current)
            if line:
                code_lines.append(line)
            # Ga naar volgende blok in de keten
            next_element = find_child(current, 'next')
            current = find_child(next_element, 'block') if next_element is not None else None

    return code_lines


def xml_to_robot(xml_text: str) -> tuple[str, str]:
    """
    Converteert Blockly XML naar Robot Framework code.
    
    Args:
        xml_text (str): Blockly workspace XML als string
    
    Returns:
        tuple: (keywords_code, robot_file)
               - keywords_code: test stappen voor live preview
               - robot_file: compleet .robot bestand
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"Ongeldige XML: {e}")
    
    code_lines = parse_blocks(root)
    keywords_code = '\n'.join(code_lines)
    
    robot_file = (
        "*** Settings ***\n"
        "Library    SeleniumLibrary\n"
        "\n"
        "*** Test Cases ***\n"
        "Generated Test\n"
        f"{keywords_code}\n"
    )
    
    return keywords_code, robot_file
