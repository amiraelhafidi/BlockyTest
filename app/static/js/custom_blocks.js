// Blockly blokken definities
Blockly.Blocks['close_browser'] = {
  init: function () {
    this.appendDummyInput()
        .appendField("Close Browser");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
  }
};

Blockly.Blocks['maximize_window'] = {
  init: function () {
    this.appendDummyInput()
        .appendField("Maximize Window");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
  }
};

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

Blockly.Blocks['assert_title'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Assert title is")
            .appendField(new Blockly.FieldTextInput("HvA"), "TITLE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(160);
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
Blockly.Python.forBlock['assert_title'] = function(block, generator) {
  const title = block.getFieldValue('TITLE');
  return `assert driver.title == "${title}"\n`;
};