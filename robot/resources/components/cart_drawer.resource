*** Settings ***
Documentation    The cart drawer that opens from the header. It is a dialog, not a route.
Resource    ../browser.resource

*** Variables ***
${CART_DRAWER}         data-testid=drawer-content
${CART_HEADING}        ${CART_DRAWER} >> role=heading[name="Cart"]
${CART_ITEM_COUNT}     ${CART_DRAWER} >> data-testid=drawer-description
# The counter's value sits in an unlabelled div right after the decrease button.
${CART_ITEM_QUANTITY}    css=button[aria-label="Decrease quantity"] + div

*** Keywords ***
Cart Drawer Should Contain Product
    [Arguments]    ${expected_name}    ${quantity}=1
    Wait For Elements State    ${CART_DRAWER}    visible
    Get Text    ${CART_HEADING}    ==    Cart
    Get Text    ${CART_ITEM_COUNT}    matches    ^${quantity} item
    # By accessible name, so a reordered drawer cannot pass with the wrong product.
    Wait For Elements State    ${CART_DRAWER} >> role=link[name="${expected_name}"]    visible
    Get Text
    ...    ${CART_DRAWER} >> css=article:has-text("${expected_name}") >> ${CART_ITEM_QUANTITY}
    ...    ==
    ...    ${quantity}
