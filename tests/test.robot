*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
Generated Test
    Open Browser    https://www.hva.nl    chrome
    Maximize Browser Window
    Sleep    3s
    Title Should Be    HvA
    Close Browser
