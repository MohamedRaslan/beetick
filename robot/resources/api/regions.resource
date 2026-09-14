*** Settings ***
Documentation    The regions call the storefront makes while loading. The header renders its
...              delivery city from it, which makes it the startup signal.
Resource    ../browser.resource

*** Variables ***
${REGIONS_MATCHER}    response => { const url = new URL(response.url()); return response.request().method() === 'GET' && url.pathname === '/milano/api/v2/regions' && url.searchParams.has('localization_code'); }

*** Keywords ***
Start Waiting For Regions Response
    # Call before navigating. Regions lands late in page load, so it gets the navigation ceiling.
    ${promise}=    Promise To    Wait For Response    matcher=${REGIONS_MATCHER}    timeout=${NAVIGATION_TIMEOUT}
    RETURN    ${promise}

Regions Response Should Be Successful
    [Arguments]    ${promise}
    ${response}=    Wait For    ${promise}
    Should Be Equal As Integers    ${response}[status]    200    Regions request failed: ${response}[url]
