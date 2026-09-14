*** Settings ***
Resource    ../browser.resource
Resource    ../assertions/image.resource

*** Variables ***
${PRODUCT_HEADING}       role=heading[level=1]
# Role selectors skip the aria-hidden duplicate in the sticky buy bar.
${ADD_TO_CART_BUTTON}    role=button[name="Add to cart"]
${DECREASE_QUANTITY}     role=button[name="Decrease quantity"]

*** Keywords ***
Opened Product Name
    ${product_name}=    Get Text    ${PRODUCT_HEADING}
    RETURN    ${product_name}

Product Image
    [Documentation]    Gallery images are labelled with the product name; index 0 is the main one.
    [Arguments]    ${index}=0
    ${product_name}=    Opened Product Name
    RETURN    role=img[name="${product_name}"] >> nth=${index}

Opened Product Should Match And Have A Loaded Image
    [Arguments]    ${expected_name}    ${index}=0
    Get Text    ${PRODUCT_HEADING}    ==    ${expected_name}
    ${image}=    Product Image    ${index}
    Image Should Be Fully Loaded    ${image}    ${expected_name}

Product Add To Cart Should Be Available
    Wait For Elements State    ${ADD_TO_CART_BUTTON}    visible
    Wait For Elements State    ${ADD_TO_CART_BUTTON}    enabled

Add Opened Product To Cart
    Click    ${ADD_TO_CART_BUTTON}

Opened Product Should Show Added Quantity
    Wait For Elements State    ${DECREASE_QUANTITY}    visible
