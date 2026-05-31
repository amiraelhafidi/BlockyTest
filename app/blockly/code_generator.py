import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


class RobotCodeGenerator:

    BLOCK_MAP = {
        "open_browser": ("Open Browser", ["URL"]),
        "maximize_window": ("Maximize Browser Window", []),
        "wait_seconds": ("Sleep", ["SECONDS"]),
        "input_text": ("Input Text", ["FIELD", "TEXT"]),
        "click_element": ("Click Element", ["ELEMENT"]),
        "wait_for_element": ("Wait Until Element Is Visible", ["ELEMENT", "TIMEOUT"]),
        "assert_title": ("Get Title", ["TITLE"]),
        "close_browser": ("Close Browser", []),
    }

    def __init__(self, xml_text):
        self.xml_text = xml_text

    def to_robot(self):
        root = ET.fromstring(self.xml_text)
        translator = RobotTranslator(root=root, block_map=self.BLOCK_MAP)
        keywords_code = "\n".join(translator.build_lines())

        return (
            "*** Settings ***\n"
            "Library    SeleniumLibrary\n"
            "\n"
            "*** Test Cases ***\n"
            "Generated Test\n"
            f"{keywords_code}\n"
        )
