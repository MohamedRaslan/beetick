*** Settings ***
Documentation    The B.TECH search-to-cart journey, in the vocabulary the tests read in.
Resource     ../browser.resource
Resource     ../api/cart.resource
Resource     ../api/regions.resource
Resource     ../components/header.resource
Resource     ../components/cart_drawer.resource
Resource     ../pages/search_results.resource
Resource     ../pages/product.resource

*** Keywords ***
Open Fresh B.TECH Browser
    New Browser    ${BROWSER}    headless=${HEADLESS}
    ${record_video_enabled}=    Convert To Boolean    ${RECORD_VIDEO}
    IF    ${record_video_enabled}
        &{video_size}=    Create Dictionary    width=${VIDEO_WIDTH}    height=${VIDEO_HEIGHT}
        &{record_video}=    Create Dictionary    dir=${OUTPUT_DIR}${/}video    size=${video_size}
        New Context    baseURL=${BEE_TICK_BASE_URL}    tracing=${TRUE}    recordVideo=${record_video}
    ELSE
        New Context    baseURL=${BEE_TICK_BASE_URL}    tracing=${TRUE}
    END
    New Page

B.TECH Home Page Is Open
    ${regions_response}=    Start Waiting For Regions Response
    Go To    ${BEE_TICK_BASE_URL}    timeout=${NAVIGATION_TIMEOUT}    wait_until=domcontentloaded
    # The header renders the city only after regions resolves, so this order is load-bearing.
    Regions Response Should Be Successful    ${regions_response}
    Header Search Should Be Ready    ${EXPECTED_DELIVERY_LOCATION}

User Searches For
    [Arguments]    ${term}
    Submit Search    ${term}
    Search Results Should Be Visible For    ${term}

First Matching Search Result Should Have An Image
    [Arguments]    ${term}
    ${product_name}=    First Matching Result Should Have An Image    ${term}
    RETURN    ${product_name}

User Opens The Selected Search Result
    Open Selected Search Result

User Adds The Opened Product To Cart
    Product Add To Cart Should Be Available
    ${offering_guid}=    Get Offering Guid From Current Url
    ${add_to_cart_response}=    Start Waiting For Add To Cart Response
    Add Opened Product To Cart
    Add To Cart Response Should Be Successful    ${add_to_cart_response}    ${offering_guid}
    Opened Product Should Show Added Quantity

User Opens The Cart
    Open Header Cart

Cart Should Contain
    [Arguments]    ${expected_name}    ${quantity}=1
    Cart Drawer Should Contain Product    ${expected_name}    ${quantity}

Close B.TECH Browser
    Run Keyword If Test Failed    Take Screenshot    filename=failure-{index}    fullPage=${TRUE}
    Close Browser    ALL
