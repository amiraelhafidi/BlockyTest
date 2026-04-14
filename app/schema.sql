CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE testflow (
    testflow_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INT NOT NULL,
    status VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (testflow_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE block (
    block_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    block_type VARCHAR(100) NOT NULL,
    position_x INT,
    position_y INT,
    sequence_number INT,
    config_json TEXT,
    PRIMARY KEY (block_id),
    FOREIGN KEY (testflow_id) REFERENCES testflow(testflow_id)
);

CREATE TABLE blockly_project (
    id INT(11) NOT NULL AUTO_INCREMENT,
    project_name VARCHAR(255) NULL,
    workspace_xml LONGTEXT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE generatedfile (
    generatedfile_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (generatedfile_id),
    FOREIGN KEY (testflow_id) REFERENCES testflow(testflow_id)
);

CREATE TABLE testrun (
    testrun_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    generatedfile_id INT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    status VARCHAR(50),
    PRIMARY KEY (testrun_id),
    FOREIGN KEY (testflow_id) REFERENCES testflow(testflow_id),
    FOREIGN KEY (generatedfile_id) REFERENCES generatedfile(generatedfile_id)
);

CREATE TABLE testreport (
    report_id INT NOT NULL AUTO_INCREMENT,
    testrun_id INT NOT NULL,
    summary TEXT,
    passed_count INT,
    failed_count INT,
    report_path VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id)
);

CREATE TABLE `projects`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT,
    PRIMARY KEY(`id`)
);
