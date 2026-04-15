"""
test_blockly_generator.py
Doel: test de Blockly XML → Robot Framework code generator functionaliteit.
Run met: python -m pytest tests/test_blockly_generator.py of python tests/test_blockly_generator.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.blockly.code_generator import xml_to_robot


def xml_block(block_type: str, **fields) -> str:
    """
    Helper: maakt een XML blok met gegeven type en fields.
    
    Args:
        block_type (str): het blockly block type (bijv. 'open_browser')
        **fields: veld naam/waarde paren (bijv. URL='https://example.com')
    
    Returns:
        str: XML string voor het blok
    """
    field_tags = ''.join(f'<field name="{k}">{v}</field>' for k, v in fields.items())
    return f'<block type="{block_type}">{field_tags}</block>'


def chain_blocks(*blocks: str) -> str:
    """
    Helper: linkt meerdere blokken aan elkaar via <next> elementen.
    
    Args:
        *blocks: variabele aantal XML bloks
    
    Returns:
        str: volledig XML met gelinkte blokken
    """
    result = blocks[-1]
    for b in reversed(blocks[:-1]):
        result = b.replace('</block>', f'<next>{result}</next></block>', 1)
    return f'<xml>{result}</xml>'


# Tests

def test_open_browser():
    """Test: open_browser blok wordt correct naar Robot geconverteerd"""
    xml = chain_blocks(xml_block('open_browser', URL='https://example.com'))
    keywords, robot = xml_to_robot(xml)
    
    assert 'Open Browser    https://example.com' in keywords
    assert '*** Settings ***' in robot
    assert 'Library    SeleniumLibrary' in robot
    print("✅ open_browser")


def test_open_browser_met_browser_type():
    """Test: open_browser met specifieke browser (chrome, firefox, etc)"""
    xml = chain_blocks(xml_block('open_browser', URL='https://test.nl', BROWSER='firefox'))
    keywords, robot = xml_to_robot(xml)
    
    assert 'Open Browser    https://test.nl    firefox' in keywords
    print("✅ open_browser_met_browser_type")


def test_open_browser_default_values():
    """Test: open_browser zonder waarden gebruikt defaults"""
    xml = chain_blocks(xml_block('open_browser'))
    keywords, _ = xml_to_robot(xml)
    
    assert 'Open Browser    https://example.com    chrome' in keywords
    print("✅ open_browser_default_values")


def test_full_chain():
    """Test: meerdere gelinkte blokken worden in volgorde geconverteerd"""
    xml = chain_blocks(
        xml_block('open_browser', URL='https://hva.nl'),
        xml_block('maximize_window'),
        xml_block('wait_seconds', SECONDS='2'),
        xml_block('assert_title', EXPECTED_TITLE='HvA'),
        xml_block('close_browser')
    )
    keywords, robot = xml_to_robot(xml)
    
    # Check of alle regels aanwezig zijn
    assert 'Open Browser    https://hva.nl' in keywords
    assert 'Maximize Browser Window' in keywords
    assert 'Sleep    2s' in keywords
    assert 'Title Should Be    HvA' in keywords
    assert 'Close Browser' in keywords
    
    # Check volgorde (eerste moet voor tweede komen)
    idx_open = keywords.find('Open Browser')
    idx_close = keywords.find('Close Browser')
    assert idx_open < idx_close, "Open Browser moet voor Close Browser komen"
    
    print("✅ full_chain")


def test_empty_xml():
    """Test: lege XML geeft lege code (behalve test case header)"""
    keywords, robot = xml_to_robot('<xml></xml>')
    assert keywords.strip() == ''
    assert '*** Test Cases ***' in robot
    assert '*** Settings ***' in robot
    print("✅ empty_xml")


def test_sleep_suffix():
    """Test: Sleep keyword krijgt automatisch 's' suffix als nodig"""
    xml = chain_blocks(xml_block('wait_seconds', SECONDS='5'))
    keywords, _ = xml_to_robot(xml)
    assert 'Sleep    5s' in keywords
    assert 'Sleep    5ss' not in keywords
    print("✅ sleep_suffix")


def test_sleep_with_existing_suffix():
    """Test: Sleep met reeds 's' suffix wordt niet verdubbeld"""
    xml = chain_blocks(xml_block('wait_seconds', SECONDS='2.5s'))
    keywords, _ = xml_to_robot(xml)
    assert 'Sleep    2.5s' in keywords
    assert 'Sleep    2.5ss' not in keywords
    print("✅ sleep_with_existing_suffix")


def test_multiple_assertions():
    """Test: meerdere assertions na elkaar"""
    xml = chain_blocks(
        xml_block('open_browser', URL='https://example.com'),
        xml_block('assert_title', EXPECTED_TITLE='Homepage'),
        xml_block('assert_title', EXPECTED_TITLE='Test Page')
    )
    keywords, _ = xml_to_robot(xml)
    
    assert 'Title Should Be    Homepage' in keywords
    assert 'Title Should Be    Test Page' in keywords
    print("✅ multiple_assertions")


def test_unknown_block_skipped():
    """Test: onbekende bloktypen worden genegeerd"""
    xml = chain_blocks(xml_block('unknown_type'))
    keywords, _ = xml_to_robot(xml)
    assert keywords.strip() == ''
    print("✅ unknown_block_skipped")


def test_mixed_known_unknown_blocks():
    """Test: mix van bekende en onbekende blokken"""
    xml = chain_blocks(
        xml_block('open_browser', URL='https://test.com'),
        xml_block('unknown_block'),
        xml_block('maximize_window'),
        xml_block('another_unknown'),
        xml_block('close_browser')
    )
    keywords, _ = xml_to_robot(xml)
    
    assert 'Open Browser    https://test.com' in keywords
    assert 'Maximize Browser Window' in keywords
    assert 'Close Browser' in keywords
    assert 'unknown_block' not in keywords
    assert 'another_unknown' not in keywords
    print("✅ mixed_known_unknown_blocks")


def test_invalid_xml():
    """Test: ongeldige XML gooit ValueError"""
    try:
        xml_to_robot('<invalid>')
        assert False, "Zou ValueError moeten gooien"
    except ValueError as e:
        assert "XML" in str(e)
        print("✅ invalid_xml")


def test_maximize_window():
    """Test: maximize_window blok"""
    xml = chain_blocks(xml_block('maximize_window'))
    keywords, _ = xml_to_robot(xml)
    assert 'Maximize Browser Window' in keywords
    print("✅ maximize_window")


def test_close_browser():
    """Test: close_browser blok"""
    xml = chain_blocks(xml_block('close_browser'))
    keywords, _ = xml_to_robot(xml)
    assert 'Close Browser' in keywords
    print("✅ close_browser")


def test_robot_file_structure():
    """Test: gegenereerd .robot bestand heeft juiste structuur"""
    xml = chain_blocks(xml_block('open_browser', URL='https://example.com'))
    _, robot = xml_to_robot(xml)
    
    # Check verplichte secties
    assert '*** Settings ***' in robot
    assert 'Library    SeleniumLibrary' in robot
    assert '*** Test Cases ***' in robot
    assert 'Generated Test' in robot
    
    # Check volgorde (Settings moet voor Test Cases komen)
    idx_settings = robot.find('*** Settings ***')
    idx_tests = robot.find('*** Test Cases ***')
    assert idx_settings < idx_tests, "Settings section moet voor Test Cases komen"
    
    print("✅ robot_file_structure")


def test_all_block_types():
    """Test: alle ondersteunde block types worden correct geconverteerd"""
    block_tests = [
        ('open_browser', {'URL': 'https://test.com'}, 'Open Browser'),
        ('maximize_window', {}, 'Maximize Browser Window'),
        ('wait_seconds', {'SECONDS': '1'}, 'Sleep'),
        ('assert_title', {'EXPECTED_TITLE': 'Test'}, 'Title Should Be'),
        ('close_browser', {}, 'Close Browser'),
    ]
    
    for block_type, fields, expected_keyword in block_tests:
        xml = chain_blocks(xml_block(block_type, **fields))
        keywords, _ = xml_to_robot(xml)
        assert expected_keyword in keywords, f"{block_type} bevat niet '{expected_keyword}'"
    
    print("✅ all_block_types")


def test_hva_workflow():
    """Test: exact workflow van test_input.xml (HvA test)"""
    # Dit is de EXACT chain uit test_input.xml van teamgenoot
    xml = chain_blocks(
        xml_block('open_browser', URL='https://www.hva.nl'),
        xml_block('maximize_window'),
        xml_block('wait_seconds', SECONDS='3'),
        xml_block('assert_title', EXPECTED_TITLE='HvA'),
        xml_block('close_browser')
    )
    
    keywords, robot = xml_to_robot(xml)
    
    # Check dat elk blok correct is geconverteerd
    assert 'Open Browser    https://www.hva.nl    chrome' in keywords
    assert 'Maximize Browser Window' in keywords
    assert 'Sleep    3s' in keywords
    assert 'Title Should Be    HvA' in keywords
    assert 'Close Browser' in keywords
    
    # Check volgorde
    idx_open = keywords.find('Open Browser')
    idx_max = keywords.find('Maximize Browser Window')
    idx_sleep = keywords.find('Sleep')
    idx_title = keywords.find('Title Should Be')
    idx_close = keywords.find('Close Browser')
    
    assert idx_open < idx_max < idx_sleep < idx_title < idx_close, \
        "Blokken zijn niet in juiste volgorde"
    
    print("✅ hva_workflow")


# ========== RUN ALL TESTS ==========

if __name__ == "__main__":
    tests = [
        # Basis tests
        test_open_browser,
        test_open_browser_met_browser_type,
        test_open_browser_default_values,
        
        # Chain en workflow tests
        test_full_chain,
        test_hva_workflow,  # ← TEAMGENOOT WORKFLOW
        
        # Empty tests
        test_empty_xml,
        
        # Sleep/wait tests
        test_sleep_suffix,
        test_sleep_with_existing_suffix,
        
        # Assertion tests
        test_multiple_assertions,
        
        # Edge cases
        test_unknown_block_skipped,
        test_mixed_known_unknown_blocks,
        test_invalid_xml,
        
        # Andere block types
        test_maximize_window,
        test_close_browser,
        
        # Structuur tests
        test_robot_file_structure,
        test_all_block_types,
    ]
    
    print("\n" + "=" * 60)
    print("BLOCKLY CODE GENERATOR TESTS - UITGEBREID")
    print("=" * 60 + "\n")
    
    passed = 0
    failed_tests = []
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed_tests.append((test.__name__, str(e)))
        except Exception as e:
            print(f"❌ {test.__name__}: {type(e).__name__}: {e}")
            failed_tests.append((test.__name__, f"{type(e).__name__}: {e}"))
    
    print("\n" + "=" * 60)
    print(f"RESULTAAT: {passed}/{len(tests)} tests geslaagd")
    if failed_tests:
        print("\nMislukte tests:")
        for name, error in failed_tests:
            print(f"  - {name}: {error}")
    print("=" * 60 + "\n")