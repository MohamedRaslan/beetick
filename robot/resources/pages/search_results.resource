*** Settings ***
Resource    ../browser.resource
Resource    ../assertions/image.resource

*** Variables ***
${RESULTS_HEADING}       role=heading[level=1]
${PRODUCT_CARD}          data-testid=product-card
${PRODUCT_CARD_TITLE}    data-testid=product-card-title
${PRODUCT_CARD_LINK}     data-testid=product-card-link
# Cards also carry a promotional badge image; the product image comes first.
${PRODUCT_CARD_IMAGE}    css=img[alt] >> nth=0
# Set by First Matching Result Should Have An Image, consumed by Open Selected Search Result.
${SELECTED_PRODUCT_CARD}    ${EMPTY}

*** Keywords ***
Search Results Should Be Visible For
    [Arguments]    ${term}
    # The site uppercases the heading with CSS and Get Text returns rendered text.
    Get Text    ${RESULTS_HEADING}    matches    (?i)^${term}$
    Get Element Count    ${PRODUCT_CARD}    >    0
    Wait For Elements State    ${PRODUCT_CARD} >> nth=0    visible

First Matching Result Should Have An Image
    [Arguments]    ${term}
    ${card}    ${title}=    Find First Matching Search Result    ${term}
    Image Should Be Present    ${card} >> ${PRODUCT_CARD_IMAGE}    ${title}
    Set Test Variable    ${SELECTED_PRODUCT_CARD}    ${card}
    RETURN    ${title}

Find First Matching Search Result
    [Documentation]    Keeps the page's own ordering but skips cards unrelated to the term.
    [Arguments]    ${term}
    Search Term Should Be Searchable    ${term}
    ${product_count}=    Get Element Count    ${PRODUCT_CARD}
    @{inspected_titles}=    Create List
    FOR    ${index}    IN RANGE    ${product_count}
        ${card}=    Set Variable    ${PRODUCT_CARD} >> nth=${index}
        ${title}=    Get Text    ${card} >> ${PRODUCT_CARD_TITLE}
        Append To List    ${inspected_titles}    ${title}
        ${matches}=    Title Matches Search Term    ${title}    ${term}
        IF    ${matches}
            Wait For Elements State    ${card}    visible
            RETURN    ${card}    ${title}
        END
    END
    ${inspected}=    Catenate    SEPARATOR=${SPACE}|${SPACE}    @{inspected_titles}
    Fail    Expected a result matching "${term}" among ${product_count} result(s): ${inspected}

Open Selected Search Result
    ${navigation}=    Promise To    Wait For Condition    Url    matches    /en/p/
    ...    timeout=${NAVIGATION_TIMEOUT}
    Click    ${SELECTED_PRODUCT_CARD} >> ${PRODUCT_CARD_LINK}
    Wait For    ${navigation}
