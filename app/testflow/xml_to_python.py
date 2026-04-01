# xml_to_python.py
# Doel: leest een Blockly XML bestand en genereert een Python testbestand en slaat het resultaat op in de database

import xml.etree.ElementTree as ET
import os


def load_xml(file_path):
    """
    Leest het XML bestand en geeft het root element terug.

    Args:
        file_path (str): pad naar het XML bestand

    Returns:
        Element: het buitenste element van het XML bestand
    """
    tree = ET.parse(file_path)
    return tree.getroot()


def block_to_python(block):
    """
    Zet één blok om naar een regel Python code.

    Args:
        block (Element): één <block> element uit het XML

    Returns:
        str: Python code regel, of None als het bloktype niet bekend is
    """
    block_type = block.get("type")

    def get_field(field_name):
        """Haalt de tekstwaarde op van een <field> element binnen dit blok."""
        for field in block.findall("field"):
            if field.get("name") == field_name:
                return field.text if field.text else ""
        return ""

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
        return None


def parse_blocks(root):
    """
    Gaat alle blokken langs en zet ze om naar Python code.

    Args:
        root (Element): het root XML element (van load_xml())

    Returns:
        list[str]: lijst met Python code regels
    """
    code_lines = []

    for block in root.iter("block"):
        python_line = block_to_python(block)
        if python_line is not None:
            code_lines.append(python_line)

    return code_lines


def write_python_test(code_lines, output_path):
    """
    Maakt een compleet testbestand. 
    Voegt de code regels toe.
    Slaat het bestand op.

    Args:
        code_lines  (list[str]): Python regels uit parse_blocks()
        output_path (str):       waar het bestand moet worden opgeslagen

    Returns:
        str: de volledige gegenereerde testcode
    """
    header = """\
import time

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

    return full_code


if __name__ == "__main__":
    from db_saver import save_test_result

    input_xml_path = "../../tests/test_input.xml"
    output_py_path = "generated_tests/test_generated.py"

    xml_root     = load_xml(input_xml_path)
    python_lines = parse_blocks(xml_root)
    generated_code = write_python_test(python_lines, output_py_path)

    save_test_result(generated_code)