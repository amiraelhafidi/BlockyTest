"""Vertaler voor XML naar Robot Framework code."""

import xml.etree.ElementTree as ET


class RobotTranslator:
    """
    Zet Blockly XML blokken om naar Robot Framework regels.

    Deze vertaler leest XML van Blockly en vertaalt elk blok naar
    een Robot Framework keyword met parameters. De blokken worden
    in volgorde verwerkt en samengesteld tot een lijst regels.
    """

    def __init__(self, root: ET.Element, block_map: dict[str, tuple[str, list[str]]]) -> None:
        """
        Maak een nieuwe vertaler voor XML blokken.

        Args:
            root (ET.Element): Root XML element van Blockly workspace
            block_map: Woordenboek dat bloktype koppelt aan Robot keyword

        Returns:
            None
        """
        self.root = root
        self.block_map = block_map
        self.code_lines: list[str] = []

    def tag_name(self, element: ET.Element) -> str:
        """
        Haal XML tagnaam op zonder namespace.

        Args:
            element (ET.Element): XML element waarvan je de naam wilt

        Returns:
            str: Tagnaam zonder namespace voorgevoegd
        """
        # XML namespaces zien er uit als "{namespace}tagname", we willen alleen "tagname"
        return element.tag.split("}")[-1]

    def child(self, element: ET.Element, tag_name: str) -> ET.Element | None:
        """
        Zoek één directe child element met deze naam.

        Args:
            element (ET.Element): Het parent XML element
            tag_name (str): Naam van het child element dat je zoekt

        Returns:
            ET.Element | None: Het gevonden element of None
        """
        for child in element:
            if self.tag_name(child) == tag_name:
                return child
        return None

    def children(self, element: ET.Element, tag_name: str) -> list[ET.Element]:
        """
        Zoek alle directe child elementen met deze naam.

        Args:
            element (ET.Element): Het parent XML element
            tag_name (str): Naam van de child elementen die je zoekt

        Returns:
            list[ET.Element]: Lijst met alle gevonden elementen
        """
        return [child for child in element if self.tag_name(child) == tag_name]

    def get_field(self, block: ET.Element, field_name: str) -> str:
        """
        Haal een veldwaarde uit een Blockly blok.

        Args:
            block (ET.Element): Het Blockly blok
            field_name (str): Naam van het veld (bijv. "URL", "SECONDS")

        Returns:
            str: De veldwaarde of lege string als niet gevonden
        """
        # Blockly blokken hebben <field> elementen met naam en waarde
        for field in self.children(block, "field"):
            if field.get("name") == field_name and field.text:
                return field.text.strip()
        return ""

    def build_line(self, block: ET.Element) -> str | None:
        """
        Zet één Blockly blok om naar één Robot Framework regel.

        Args:
            block (ET.Element): Het Blockly blok om om te zetten

        Returns:
            str | None: Robot regel als bekend bloktype, anders None
        """
        block_type = block.get("type")

        # Controleer of dit bloktype bekend is in BLOCK_MAP
        if block_type not in self.block_map:
            return None

        # Haal keyword en veldnamen op uit de mapping
        keyword, fields = self.block_map[block_type]
        # Verzamel alle veldwaarden voor dit blok
        args = [self.get_field(block, field_name) for field_name in fields]

        # Robot Framework Sleep keyword moet eindigen met "s" voor seconden
        if block_type == "wait_seconds" and args and not args[0].endswith("s"):
            args[0] += "s"

        # Bouw de regel: keyword + arguments met juiste indentatie
        parts = [keyword] + args
        return "    " + "    ".join(parts)

    def build_lines(self) -> list[str]:
        """
        Zet alle Blockly blokken om naar Robot Framework regels.

        Returns:
            list[str]: Alle Robot regels in volgorde
        """
        self.code_lines = []

        # Blokken vormen ketens: elk blok kan een "next" element hebben met het volgende blok
        # We verwerken alle top-level blokken en volgen de ketens
        for top_block in self.children(self.root, "block"):
            current = top_block
            # Volg de blokketen tot het einde
            while current is not None:
                line = self.build_line(current)
                if line:
                    self.code_lines.append(line)

                # Zoek het volgende blok in de keten via het <next> element
                next_element = self.child(current, "next")
                current = self.child(next_element, "block") if next_element is not None else None

        return self.code_lines
