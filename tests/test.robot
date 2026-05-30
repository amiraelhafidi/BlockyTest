*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
Generated Test
    Open Browser    https://www.hva.nl    chrome
    Maximize Browser Window
    Sleep    3s
    ${title}=    Get Title
    Should Contain    ${title}    HvA
    Close Browser
