from app.blockly.code_generator import xml_to_robot


def test_open_browser_blok_vertaalt_correct():
    # Simuleert een Blockly editor met één blok: Open Browser
    # Dit is dezelfde XML die de editor verstuurt als een gebruiker een blok plaatst
    xml = '<xml><block type="open_browser"><field name="URL">https://www.hva.nl</field></block></xml>'
    _, robot_file = xml_to_robot(xml)
    # Controleert of de vertaling de juiste Robot Framework keyword bevat
    assert "Open Browser    https://www.hva.nl" in robot_file
