"""Genereer Robot Framework code uit Blockly XML."""

import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


class CodeGenerator:
    """
    Genereer Robot Framework test code uit Blockly XML.

    Deze klasse vertaalt Blockly workspace XML naar volledige Robot Framework
    test bestanden. Ze verzorgt de XML parsing, blok vertaling en test template
    generatie. BLOCK_MAP bevat alle beschikbare blok types.
    """

    # Vertaling van Blockly bloktypen naar Robot Framework keywords
    # Format: "blockly_type": ("Robot keyword", [veldnamen])
    BLOCK_MAP = {
        "open_browser": ("Open Browser", ["URL", "BROWSER"]),
        "maximize_window": ("Maximize Browser Window", []),
        "wait_seconds": ("Sleep", ["SECONDS"]),
        "assert_title": ("Title Should Be", ["TITLE"]),
        "close_browser": ("Close Browser", []),
    }

    def xml_to_robot(self, xml_text: str) -> tuple[str, str]:
        """
        Vertaal Blockly XML naar Robot Framework code.

        Deze methode zet de XML van Blockly blokken om naar Robot Framework
        test code. Eerst worden de blokken vertaald naar Robot keywords via
        RobotTranslator. Daarna wordt alles samengesteld in een volledig
        .robot bestand met Settings en Test Cases secties.

        Args:
            xml_text (str): Blockly workspace XML string

        Returns:
            tuple[str, str]: (keywords_code, robot_file)
                - keywords_code: De gegenereerde Robot Framework keywords
                - robot_file: Het volledige .robot bestand met template

        """
        # Zet XML string om naar ET object
        root = ET.fromstring(xml_text)

        # Vertaal blokken naar Robot regels via RobotTranslator
        translator = RobotTranslator(root=root, block_map=self.BLOCK_MAP)
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


# Backward compatibility - oude code blijft werken
_generator = CodeGenerator()
xml_to_robot = _generator.xml_to_robot
