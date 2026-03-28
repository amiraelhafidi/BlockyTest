# xml_to_python.py
# Doel: leest een Blockly XML bestand en genereert een Python testbestand

import xml.etree.ElementTree as ET
import os

BLOCKLY_NAMESPACE = "https://developers.google.com/blockly/xml"


def load_xml(file_path):
    """
    Opent het XML bestand en geeft het root element terug.

    Args:
        file_path (str): pad naar het .xml bestand

    Returns:
        Element: het buitenste XML element
    """
    tree = ET.parse(file_path)
    return tree.getroot()


def block_to_python(block):
    """
    Vertaalt één Blockly blok naar één Python code regel.

    Args:
        block (Element): één XML <block> element

    Returns:
        str: één Python code regel, of None als het bloktype onbekend is
    """
    block_type = block.get("type")

    def get_field(field_name):
        """Haalt de tekstwaarde op van een <field> element binnen dit blok."""
        field = block.find(f"{{{BLOCKLY_NAMESPACE}}}field[@name='{field_name}']")
        return field.text if field is not None else ""

    if block_type == "open_browser":
        url = get_field("URL")
        return f'        driver.get("{url}")'

    elif block_type == "maximize_window":
        return f'        driver.maximize_window()'

    elif block_type == "wait_seconds":
        seconds = get_field("SECONDS")
        return f'        time.sleep({seconds})'

    elif block_type == "assert_title":
        expected_title = get_field("EXPECTED_TITLE")
        return f'        assert "{expected_title}" in driver.title'

    elif block_type == "close_browser":
        return f'        driver.quit()'

    elif block_type == "click_element":
        selector = get_field("SELECTOR")
        return f'        driver.find_element(By.CSS_SELECTOR, "{selector}").click()'

    elif block_type == "assert_text":
        selector = get_field("SELECTOR")
        expected_text = get_field("EXPECTED_TEXT")
        return f'        assert driver.find_element(By.CSS_SELECTOR, "{selector}").text == "{expected_text}"'

    else:
        print(f"  [WAARSCHUWING] Onbekend bloktype: '{block_type}'")
        return None


def parse_blocks(root):
    """
    Loopt door alle blokken in de XML boom en vertaalt ze naar Python regels.

    Args:
        root (Element): het root XML element van load_xml()

    Returns:
        list[str]: lijst van Python code regels
    """
    code_lines = []

    for block in root.iter(f"{{{BLOCKLY_NAMESPACE}}}block"):
        python_line = block_to_python(block)
        if python_line is not None:
            code_lines.append(python_line)

    return code_lines


def write_python_test(code_lines, output_path):
    """
    Schrijft de gegenereerde code regels weg als een compleet Python testbestand.

    Args:
        code_lines (list[str]): Python regels van parse_blocks()
        output_path (str): waar het .py bestand opgeslagen wordt
    """
    header = """\
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def test_generated():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    try:
"""
    footer = """\

    finally:
        driver.quit()
"""
    full_code = header
    for line in code_lines:
        full_code += line + "\n"
    full_code += footer

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as output_file:
        output_file.write(full_code)

    print(f"[OK] Testbestand aangemaakt: {output_path}")


if __name__ == "__main__":
    input_xml_path = "../../tests/test_input.xml"    # ← aangepast
    output_py_path = "generated_tests/test_generated.py"

    xml_root = load_xml(input_xml_path)
    python_lines = parse_blocks(xml_root)
    write_python_test(python_lines, output_py_path)