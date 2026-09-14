*** Settings ***
Documentation    The site header, present on every route.
Resource    ../browser.resource

*** Variables ***
# Two responsive copies of the input are rendered; only one is visible.
${SEARCH_INPUT}          data-testid=search-input >> visible=true
${HEADER_CART_BUTTON}    role=button[name="Cart"]
${DELIVERY_LOCATION}     text=/^Delivering to:/i >> visible=true
# Regions has resolved once a city follows the label. Backslashes are doubled for Robot.
${DELIVERY_LOCATION_RESOLVED}    (?i)^Delivering to:\\s*\\S+

*** Keywords ***
Header Search Should Be Ready
    Get Text    ${DELIVERY_LOCATION}    matches    ${DELIVERY_LOCATION_RESOLVED}
    Wait For Elements State    ${SEARCH_INPUT}    editable

Submit Search
    [Arguments]    ${term}
    Fill Text    ${SEARCH_INPUT}    ${term}
    ${navigation}=    Promise To    Wait For Condition    Url    matches    /en/s[?].*q=${term}(&|$)
    ...    timeout=${NAVIGATION_TIMEOUT}
    # Pressed on the input so an open suggestion cannot swallow the Enter.
    Press Keys    ${SEARCH_INPUT}    Enter
    Wait For    ${navigation}

Open Header Cart
    Click    ${HEADER_CART_BUTTON}
