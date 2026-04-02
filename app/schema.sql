CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
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
    PRIMARY KEY (testflow_id)
);

CREATE TABLE block (
    block_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    block_type VARCHAR(100) NOT NULL,
    label VARCHAR(255),
    position_x INT,
    position_y INT,
    sequence_number INT,
    config_json TEXT,
    PRIMARY KEY (block_id)
);

CREATE TABLE generatedfile (
    generatedfile_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (generatedfile_id)
);

CREATE TABLE testrun (
    testrun_id INT NOT NULL AUTO_INCREMENT,
    testflow_id INT NOT NULL,
    generatedfile_id INT,
    started_by INT NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    status VARCHAR(50),
    PRIMARY KEY (testrun_id)
);

CREATE TABLE testreport (
    report_id INT NOT NULL AUTO_INCREMENT,
    testrun_id INT NOT NULL,
    summary TEXT,
    passed_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    report_path VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id)
);