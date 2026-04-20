<!-- Legenda:
    + = public: zichtbaar en toegankelijk van buiten de class
    - = private: alleen toegankelijk binnen de class zelf
    # = protected: toegankelijk binnen de class en in subclasses
-->

class Project {
    +int testflow_id
    +str name
    +str description
    +str status
    +str created_at
    +list validation_errors
    +dict display_data
    +__init__(testflow_id, name, description, status, created_at)
    +is_valid() bool
    +to_template_dict() dict
    +from_row(row) Project
}

class ProjectRepository {
    +get_all() list~Project~
    +get_by_id(project_id) Project
    +create(project) dict
    +update(project) dict
    +delete(project_id) dict
}

class ProjectForm {
    +dict form_data
    +list errors
    +dict cleaned_data
    +__init__(form_data)
    +validate() bool
    +to_project(testflow_id, status) Project
}

ProjectRepository ..> Project : creates from database rows
ProjectForm ..> Project : creates from form data


class CodeGenerator {
    +dict BLOCK_MAP
    +xml_to_robot(xml_text: str) tuple[str, str]
}

class RobotTranslator {
    +ET.Element root
    +dict block_map
    +list[str] code_lines
    +__init__(root: ET.Element, block_map: dict)
    +tag_name(element: ET.Element) str
    +child(element: ET.Element, tag_name: str) ET.Element | None
    +children(element: ET.Element, tag_name: str) list[ET.Element]
    +get_field(block: ET.Element, field_name: str) str
    +build_line(block: ET.Element) str | None
    +build_lines() list[str]
}

class TestResult {
    +int return_code
    +dict[str, int] counts
    +list[str] output_lines
    +__init__(return_code: int, counts: dict, output_lines: list)
    +from_process(result: subprocess.CompletedProcess) TestResult
    +to_dict(error_output: str) dict
}

CodeGenerator ..> RobotTranslator : uses

