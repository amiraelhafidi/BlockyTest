from app.blockly.code_generator import xml_to_robot


def test_open_browser_genereert_juiste_code():
    xml = '<xml><block type="open_browser"><field name="URL">https://www.hva.nl</field></block></xml>'
    _, robot_file = xml_to_robot(xml)
    assert "Open Browser    https://www.hva.nl" in robot_file
