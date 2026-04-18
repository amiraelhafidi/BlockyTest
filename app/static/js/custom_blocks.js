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
        .appendField("Assert title")
        .appendField(new Blockly.FieldTextInput("HvA"), "TITLE");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
  }
};

Blockly.Python.forBlock['assert_title'] = function(block) {
  const title = block.getFieldValue('TITLE');
  return `assert driver.title == ${JSON.stringify(title)}\n`;
};

Blockly.Python.forBlock['wait_seconds'] = function(block) {
  const seconds = block.getFieldValue('SECONDS');
  return `time.sleep(${seconds})\n`;
};

// Code generators
Blockly.Python.forBlock['close_browser'] = function(block) {
  return 'driver.close()\n';
};

Blockly.Python.forBlock['maximize_window'] = function(block) {
  return 'driver.maximize_window()\n';
};
