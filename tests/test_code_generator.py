from app.blockly.code_generator import RobotCodeGenerator


def test_open_browser_blok_vertaalt_correct():
    """
    Simuleert een Blockly editor met één blok: Open Browser.
    Controleert of de vertaling de juiste Robot Framework keyword bevat.
    """
    # Maak de XML na die Blockly opslaat: één Open Browser-blok met een URL erin.
    xml = '<xml><block type="open_browser"><field name="URL">https://www.hva.nl</field></block></xml>'

    # Laat de generator er een Robot-testbestand van maken.
    robot_file = RobotCodeGenerator(xml).to_robot()

    # Controleer dat het juiste keyword met de URL in het bestand staat.
    assert "Open Browser    https://www.hva.nl" in robot_file
