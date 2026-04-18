"""Vertaler voor XML naar Robot Framework code."""

import xml.etree.ElementTree as ET


class RobotTranslator:
    """
    Vertaalt Blocky XML naar Robot Framework code.

    Attributes:
        root (ET.Element): Het root XML element.
        block_map (dict[str, tuple[str, list[str]]]): Koppeling van bloktype naar keyword.
        code_lines (list[str]): Opgebouwde Robot regels.
    """

    def __init__(self, root: ET.Element, block_map: dict[str, tuple[str, list[str]]]) -> None:
        """
        Maakt een nieuwe vertaler.

        Args:
            root (ET.Element): Het root XML element.
            block_map (dict[str, tuple[str, list[str]]]): Koppeling van bloktype naar keyword.

        Returns:
            None: Deze constructor geeft niets terug.
        """
        self.root = root
        self.block_map = block_map
        self.code_lines: list[str] = []

    def tag_name(self, element: ET.Element) -> str:
        """
        Geeft de tagnaam terug zonder XML namespace.

        Args:
            element (ET.Element): XML element waarvan de tag nodig is.

        Returns:
            str: Tagnaam zonder namespace.
        """
        return element.tag.split("}")[-1]

    def child(self, element: ET.Element, tag_name: str) -> ET.Element | None:
        """
        Zoekt een direct child element op tagnaam.

        Args:
            element (ET.Element): Het parent XML element.
            tag_name (str): De gezochte tagnaam.

        Returns:
            ET.Element | None: Het gevonden child element of None.
        """
        for child in element:
            if self.tag_name(child) == tag_name:
                return child
        return None

    def children(self, element: ET.Element, tag_name: str) -> list[ET.Element]:
        """
        Zoekt alle directe child elementen op tagnaam.

        Args:
            element (ET.Element): Het parent XML element.
            tag_name (str): De gezochte tagnaam.

        Returns:
            list[ET.Element]: Lijst met gevonden child elementen.
        """
        return [child for child in element if self.tag_name(child) == tag_name]

    def get_field(self, block: ET.Element, field_name: str) -> str:
        """
        Haalt de waarde van een veld uit een blok.

        Args:
            block (ET.Element): Het Blocky blok.
            field_name (str): Naam van het veld.

        Returns:
            str: De veldwaarde of een lege string.
        """
        for field in self.children(block, "field"):
            if field.get("name") == field_name and field.text:
                return field.text.strip()
        return ""

    def build_line(self, block: ET.Element) -> str | None:
        """
        Zet één blok om naar één Robot regel.

        Args:
            block (ET.Element): Het Blocky blok.

        Returns:
            str | None: De Robot regel of None bij een onbekend blok.
        """
        block_type = block.get("type")

        if block_type not in self.block_map:
            # Onbekende blokken slaan we over.
            return None

        keyword, fields = self.block_map[block_type]
        args = [self.get_field(block, field_name) for field_name in fields]

        # Sleep moet altijd eindigen op seconden.
        if block_type == "wait_seconds" and args and not args[0].endswith("s"):
            args[0] += "s"

        parts = [keyword] + args
        return "    " + "    ".join(parts)

    def build_lines(self) -> list[str]:
        """
        Leest alle blokken in de workspace en zet ze om naar Robot regels.

        Returns:
            list[str]: Lijst met Robot regels.
        """
        self.code_lines = []

        for top_block in self.children(self.root, "block"):
            # Loop door de hele blokketen via <next>.
            current = top_block
            while current is not None:
                line = self.build_line(current)
                if line:
                    self.code_lines.append(line)

                # Pak het volgende blok uit de keten.
                next_element = self.child(current, "next")
                current = self.child(next_element, "block") if next_element is not None else None

        return self.code_lines
