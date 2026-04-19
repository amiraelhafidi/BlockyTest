"""Zet Blocky XML om naar Robot Framework code."""

import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


# Vertaling van Blockly bloktypen naar Robot Framework keywords
# Format: "blockly_type": ("Robot keyword", [veldnamen])
BLOCK_MAP = {
    "open_browser": ("Open Browser", ["URL", "BROWSER"]),
    "maximize_window": ("Maximize Browser Window", []),
    "wait_seconds": ("Sleep", ["SECONDS"]),
    "assert_title": ("Title Should Be", ["TITLE"]),
    "close_browser": ("Close Browser", []),
}


def xml_to_robot(xml_text: str) -> tuple[str, str]:
    """
    Vertaal Blockly XML naar Robot Framework code.

    Deze functie zet de XML van Blockly blokken om naar Robot Framework
    test code. Eerst worden de blokken vertaald naar Robot keywords.
    Daarna wordt alles samengesteld in een .robot bestand.

    Args:
        xml_text (str): Blockly workspace XML string

    Returns:
        tuple[str, str]: (keywords_code, robot_file)
            - keywords_code: De Robot Framework keywords (alleen keywords)
            - robot_file: Het volledige .robot bestand met template
    """
    # Zet XML string om naar ET object
    root = ET.fromstring(xml_text)

    # Vertaal blokken naar Robot regels
    translator = RobotTranslator(root=root, block_map=BLOCK_MAP)
    code_lines = translator.build_lines()
    keywords_code = "\n".join(code_lines)

    # Maak volledig .robot bestand met Robot Framework template
    robot_file = (
        "*** Settings ***\n"
        "Library    SeleniumLibrary\n"
        "\n"
        "*** Test Cases ***\n"
        "Generated Test\n"
        f"{keywords_code}\n"
    )

    return keywords_code, robot_file
