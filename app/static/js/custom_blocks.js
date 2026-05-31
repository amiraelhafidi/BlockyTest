// Custom blocks for browser actions



// Custom block to click on an element identified by its name attribute
Blockly.Blocks['click_element'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Click Element")
            .appendField(new Blockly.FieldTextInput("loginButton"), "ELEMENT");

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F2994A");
    }
};


// Custom block to open the browser with a specified URL
Blockly.Blocks['open_browser'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Open Browser")
            .appendField(new Blockly.FieldTextInput("https://example.com"), "URL");

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#2D9CDB");
    }
};

// Custom blocks to close the browser
Blockly.Blocks['close_browser'] = {
  init: function () {
    this.appendDummyInput()
        .appendField("Close Browser");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#2D9CDB");
  }
};

// Custom block to maximize the browser window
Blockly.Blocks['maximize_window'] = {
  init: function () {
    this.appendDummyInput()
        .appendField("Maximize Window");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#2D9CDB");
  }
};

// Custom blocks to wait for a certain number of seconds
Blockly.Blocks['wait_seconds'] = {
  init: function () {
    this.appendDummyInput()
        .appendField("Wait")
        .appendField(new Blockly.FieldNumber(1, 0), "SECONDS")
        .appendField("seconds");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
  }
};

// Custom block to assert the browser title
Blockly.Blocks['assert_title'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Title should contain")
            .appendField(new Blockly.FieldTextInput(""), "TITLE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(160);
    }
};


// Custom block to input text into a field identified by its name attribute
Blockly.Blocks['input_text'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Input Text")
            .appendField(new Blockly.FieldTextInput("username"), "FIELD")
            .appendField(new Blockly.FieldTextInput("tekst"), "TEXT");

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F2994A");
    }
};

// Custom block om te wachten op een element
Blockly.Blocks['wait_for_element'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Wait For Element")
            .appendField(new Blockly.FieldTextInput("loginButton"), "ELEMENT");

        this.appendDummyInput()
            .appendField("Timeout")
            .appendField(new Blockly.FieldNumber(10, 1), "TIMEOUT");

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F2994A");
    }
};

// Custom block to capture a screenshot
Blockly.Blocks['capture_screenshot'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Capture Screenshot");

    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#F2994A");
  }
};



// Python Code Generators 

// Genereert Python code om de browser te sluiten
Blockly.Python.forBlock['close_browser'] = function(block, generator) {
  return 'driver.quit()\n';
};

// Genereert Python code om het browser venster te maximaliseren
Blockly.Python.forBlock['maximize_window'] = function(block, generator) {
  return 'driver.maximize_window()\n';
};

// Genereert Python code om te wachten voor een bepaald aantal seconden
Blockly.Python.forBlock['wait_seconds'] = function(block, generator) {
  const seconds = block.getFieldValue('SECONDS');
  return `time.sleep(${seconds})\n`;
};

// Genereert Python code om de browser titel te controleren
Blockly.Python.forBlock['open_browser'] = function(block, generator) {

    const url = block.getFieldValue('URL');

    return `
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("${url}")
`;
};

// Genereert Python code om de browser te openen met de gegeven URL
Blockly.Python.forBlock['open_browser'] = function(block, generator) {
    const url = block.getFieldValue('URL');
    return `driver.get("${url}")\n`;
};

// Generates Python code to input text into a field identified by its name attribute
Blockly.Python.forBlock['input_text'] = function(block, generator) {
    const field = block.getFieldValue('FIELD');
    const text = block.getFieldValue('TEXT');

    return `driver.find_element(By.NAME, "${field}").send_keys("${text}")\n`;
};

// Generates selenium code to click on an element identified by its name attribute
Blockly.Python.forBlock['click_element'] = function(block, generator) {
    const element = block.getFieldValue('ELEMENT');

    return `driver.find_element(By.NAME, "${element}").click()\n`;
};

// Genereert Selenium code om te wachten op een element
Blockly.Python.forBlock['wait_for_element'] = function(block, generator) {

    const element = block.getFieldValue('ELEMENT');
    const timeout = block.getFieldValue('TIMEOUT');

    return `
WebDriverWait(driver, ${timeout}).until(
    EC.presence_of_element_located((By.NAME, "${element}"))
)
`;
};

// Genereert Selenium code om de browser titel te controleren
Blockly.Python.forBlock['assert_title'] = function(block, generator) {
    const title = block.getFieldValue('TITLE');
    return `assert "${title}" == driver.title\n`;
};

// Genereert Selenium code om een screenshot te maken
Blockly.Python.forBlock['capture_screenshot'] = function(block, generator) {
  return `driver.save_screenshot("screenshot.png")\n`;
};

