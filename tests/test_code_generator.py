from app.blockly.code_generator import RobotCodeGenerator


def test_open_browser_blok_vertaalt_correct():
    """
    Simuleert een Blockly editor met één blok: Open Browser.
    Controleert of de vertaling de juiste Robot Framework keyword bevat.
    """
    xml = '<xml><block type="open_browser"><field name="URL">https://www.hva.nl</field></block></xml>'
    robot_file = RobotCodeGenerator(xml).to_robot()
    assert "Open Browser    https://www.hva.nl" in robot_file
