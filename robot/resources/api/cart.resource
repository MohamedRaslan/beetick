*** Settings ***
Documentation    The add-to-cart mutation: the one backend contract this journey asserts.
Resource    ../browser.resource

*** Variables ***
${ADD_TO_CART_MATCHER}    response => { const url = new URL(response.url()); return response.request().method() === 'POST' && url.pathname.endsWith('/blink/api/v4/carts/add-to-cart'); }

*** Keywords ***
Get Offering Guid From Current Url
    ${url}=    Get Url
    ${offering_guid}=    Get Offering Guid From Url    ${url}
    RETURN    ${offering_guid}

Start Waiting For Add To Cart Response
    # Call before clicking add-to-cart.
    ${promise}=    Promise To    Wait For Response    matcher=${ADD_TO_CART_MATCHER}    timeout=${NETWORK_TIMEOUT}
    RETURN    ${promise}

Add To Cart Response Should Be Successful
    [Arguments]    ${promise}    ${offering_guid}    ${quantity}=1
    ${response}=    Wait For    ${promise}
    Should Be Equal As Integers    ${response}[status]    200    Add-to-cart request failed: ${response}[url]
    Add To Cart Response Should Be Valid    ${response}    ${offering_guid}    ${quantity}
