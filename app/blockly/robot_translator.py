import xml.etree.ElementTree as ET


class RobotTranslator:

    def __init__(self, root, block_map):
        self.root = root
        self.block_map = block_map

    def tag_name(self, element):
        return element.tag.split("}")[-1]

    def child(self, element, tag_name):
        for child in element:
            if self.tag_name(child) == tag_name:
                return child
        return None

    def children(self, element, tag_name):
        return [child for child in element if self.tag_name(child) == tag_name]

    def get_field(self, block, field_name):
        for field in self.children(block, "field"):
            if field.get("name") == field_name and field.text:
                return field.text.strip()
        return ""

    def build_line(self, block):
        block_type = block.get("type")

        if block_type not in self.block_map:
            return None

        keyword, fields = self.block_map[block_type]
        args = [self.get_field(block, f) for f in fields]

        if block_type == "wait_seconds" and args and not args[0].endswith("s"):
            args[0] += "s"

        if block_type == "assert_title":
            return f"    ${{title}}=    Get Title\n    Should Contain    ${{title}}    {args[0]}"

        return "    " + "    ".join([keyword] + args)

    def build_lines(self):
        lines = []

        for top_block in self.children(self.root, "block"):
            current = top_block
            while current is not None:
                line = self.build_line(current)
                if line:
                    lines.append(line)
                next_element = self.child(current, "next")
                current = self.child(next_element, "block") if next_element is not None else None

        return lines