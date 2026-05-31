import xml.etree.ElementTree as ET

from app.blockly.robot_translator import RobotTranslator


class RobotCodeGenerator:
    """Zet de blokken uit de Blockly-editor om in een Robot Framework-testbestand.

    De gebruiker bouwt zijn test met blokken. Blockly slaat die blokken op als
    XML. Deze klasse leest die XML en maakt er een werkend .robot-bestand van.
    """

    # Koppelt elk Blockly-blok aan een Robot Framework-keyword.
    # Per blok: (naam van het keyword, lijst met velden die het blok meegeeft).
    BLOCK_MAP = {
        "open_browser": ("Open Browser", ["URL"]),
        "maximize_window": ("Maximize Browser Window", []),
        "wait_seconds": ("Sleep", ["SECONDS"]),
        "input_text": ("Input Text", ["FIELD", "TEXT"]),
        "click_element": ("Click Element", ["ELEMENT"]),
        "wait_for_element": ("Wait Until Element Is Visible", ["ELEMENT", "TIMEOUT"]),
        "assert_title": ("Title Should Be", ["TITLE"]),
        "capture_screenshot": ("Capture Page Screenshot", []),
        "close_browser": ("Close Browser", []),
    }

    def __init__(self, xml_text):
        """Bewaar de XML uit de Blockly-editor.

        Args:
            xml_text (str): De blokken als XML-tekst, zoals Blockly die opslaat.
        """
        self.xml_text = xml_text

    def to_robot(self):
        """Bouw het complete Robot Framework-testbestand op.

        Leest de XML, laat de RobotTranslator er testregels van maken

        Returns:
            str: De volledige inhoud van een .robot-bestand, klaar om te draaien.
        """
        # Lees de XML-tekst in als een boomstructuur waar we doorheen kunnen lopen.
        root = ET.fromstring(self.xml_text)

        # Vertaal de blokken naar losse Robot-regels en plak ze onder elkaar.
        translator = RobotTranslator(root=root, block_map=self.BLOCK_MAP)
        keywords_code = "\n".join(translator.build_lines())

        # Zet de vertaalde regels in een vast sjabloon van een Robot-testbestand.
        return (
            "*** Settings ***\n"
            "Library    SeleniumLibrary\n"
            "\n"
            "*** Test Cases ***\n"
            "Generated Test\n"
            f"{keywords_code}\n"
        )
