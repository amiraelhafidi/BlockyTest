class RobotTranslator:
    """Loopt door de Blockly-XML en maakt van elk blok een Robot-testregel.

    De RobotCodeGenerator geeft deze klasse de XML-boom en de BLOCK_MAP.
    Deze klasse zoekt de blokken op, leest hun velden uit en zet ze om in
    tekstregels die Robot Framework begrijpt.
    """

    def __init__(self, root, block_map):
        """Bewaar de XML-boom en de tabel met blok-vertalingen.

        Args:
            root: Het bovenste XML-element (de hele blokkenboom).
            block_map (dict): Koppelt elk bloktype aan een keyword en zijn velden.
        """
        self.root = root
        self.block_map = block_map

    def tag_name(self, element):
        """Geef de naam van een XML-element zonder de namespace ervoor.

        Args:
            element: Een XML-element.

        Returns:
            str: De tagnaam zonder namespace.
        """
        return element.tag.split("}")[-1]

    def child(self, element, tag_name):
        """Zoek het eerste directe kind met een bepaalde tagnaam.

        Args:
            element: Het XML-element waarin we zoeken.
            tag_name (str): De tagnaam die we willen vinden, bijvoorbeeld "next".

        Returns:
            Het eerste passende kind-element, of None als er geen is.
        """
        for child in element:
            if self.tag_name(child) == tag_name:
                return child
        return None

    def children(self, element, tag_name):
        """Zoek alle directe kinderen met een bepaalde tagnaam.

        Args:
            element: Het XML-element waarin we zoeken.
            tag_name (str): De tagnaam die we willen vinden, bijvoorbeeld "block".

        Returns:
            list: Alle passende kind-elementen (kan leeg zijn).
        """
        return [child for child in element if self.tag_name(child) == tag_name]

    def get_field(self, block, field_name):
        """Lees de waarde van één veld uit een blok.

        Args:
            block: Het blok-element.
            field_name (str): De naam van het veld dat we zoeken.

        Returns:
            str: De ingevulde waarde, of een lege tekst als het veld leeg is.
        """
        for field in self.children(block, "field"):
            if field.get("name") == field_name and field.text:
                return field.text.strip()
        return ""

    def build_line(self, block):
        """Maak van één blok één Robot-testregel.

        Zoekt het juiste keyword op in de block_map, leest de velden uit en zet
        ze samen tot een regel. Twee blokken hebben een uitzondering nodig:
        - wait_seconds: hier plakken we een "s" achter het getal (bv. "5s").
        - assert_title: hier maken we twee regels om de titel te controleren.

        Args:
            block: Het blok-element dat we willen vertalen.

        Returns:
            str: De Robot-testregel(s), of None als het bloktype onbekend is.
        """
        block_type = block.get("type")

        # Onbekend bloktype: dit blok slaan we over.
        if block_type not in self.block_map:
            return None

        # Haal het keyword en de bijbehorende velden op en lees de waarden uit.
        keyword, fields = self.block_map[block_type]
        args = [self.get_field(block, f) for f in fields]

        # Sleep verwacht een tijd zoals "5s"; zet de "s" erachter als die mist.
        if block_type == "wait_seconds" and args and not args[0].endswith("s"):
            args[0] += "s"

        # De titel controleren we in twee stappen: ophalen en dan vergelijken.
        if block_type == "assert_title":
            return f"    ${{title}}=    {keyword}\n    Should Contain    ${{title}}    {args[0]}"

        # Normaal geval: keyword en argumenten met tabs (vier spaties) ertussen.
        return "    " + "    ".join([keyword] + args)

    def build_lines(self):
        """Zet alle blokken om in een lijst Robot-testregels, in de juiste volgorde.

        Blokken zitten aan elkaar vast via een "next"-element. We beginnen bij
        elk bovenste blok en volgen telkens de keten naar het volgende blok,
        net zolang tot er geen volgend blok meer is.

        Returns:
            list: De testregels op volgorde, klaar om in het bestand te zetten.
        """
        lines = []

        # Begin bij elk los bovenste blok in de werkruimte.
        for top_block in self.children(self.root, "block"):
            current = top_block
            # Volg de keten van blok naar blok totdat er geen volgend blok meer is.
            while current is not None:
                line = self.build_line(current)
                if line:
                    lines.append(line)
                # Ga naar het volgende blok dat onder het huidige blok hangt.
                next_element = self.child(current, "next")
                current = self.child(next_element, "block") if next_element is not None else None

        return lines
