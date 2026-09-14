*** Settings ***
Documentation      B.TECH search-to-cart end-to-end coverage.
Resource           ../resources/flows/btech_flow.resource
Test Setup         Open Fresh B.TECH Browser
Test Teardown      Close B.TECH Browser
Test Timeout       60s

*** Variables ***
${SEARCH_TERM}    iphone17

*** Test Cases ***
Add First Matching iPhone17 Search Result To Cart
    [Documentation]    Verifies the required B.TECH search-to-cart journey.
    [Tags]    smoke    e2e    ui    cart
    Given B.TECH Home Page Is Open
    When User Searches For    ${SEARCH_TERM}
    ${product_name}=    Then First Matching Search Result Should Have An Image    ${SEARCH_TERM}
    When User Opens The Selected Search Result
    Then Opened Product Should Match And Have A Loaded Image    ${product_name}
    When User Adds The Opened Product To Cart
    And User Opens The Cart
    Then Cart Should Contain    ${product_name}
