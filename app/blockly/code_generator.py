"""Zet Blocky XML om naar Robot Framework code."""

import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


# Koppelt een bloktype aan een Robot keyword en de velden die nodig zijn.
BLOCK_MAP = {
    "open_browser": ("Open Browser", ["URL", "BROWSER"]),
    "maximize_window": ("Maximize Browser Window", []),
    "wait_seconds": ("Sleep", ["SECONDS"]),
    "assert_title": ("Title Should Be", ["TITLE"]),
    "close_browser": ("Close Browser", []),
}


def xml_to_robot(xml_text: str) -> tuple[str, str]:
    """
    Converteert Blocky XML naar Robot Framework code.

    Args:
        xml_text (str): De Blocky workspace als XML string.

    Returns:
        tuple[str, str]: Preview code en volledig Robot bestand.
    """
    root = ET.fromstring(xml_text)

    # Gebruik de translator class om de regels op te bouwen.
    translator = RobotTranslator(root=root, block_map=BLOCK_MAP)
    code_lines = translator.build_lines()
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
