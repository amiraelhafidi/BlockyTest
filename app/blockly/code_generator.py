import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


BLOCK_MAP = {
    "open_browser": ("Open Browser", ["URL"]),
    "maximize_window": ("Maximize Browser Window", []),
    "wait_seconds": ("Sleep", ["SECONDS"]),
    "assert_title": ("Title Should Contain", ["TITLE"]),
    "close_browser": ("Close Browser", []),
}


def xml_to_robot(xml_text):
    root = ET.fromstring(xml_text)
    translator = RobotTranslator(root=root, block_map=BLOCK_MAP)
    keywords_code = "\n".join(translator.build_lines())

    robot_file = (
        "*** Settings ***\n"
        "Library    SeleniumLibrary\n"
        "Suite Teardown    Close All Browsers\n"
        "\n"
        "*** Test Cases ***\n"
        "Generated Test\n"
        f"{keywords_code}\n"
    )

    return keywords_code, robot_file