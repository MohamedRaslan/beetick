*** Settings ***
Documentation    Image checks. Both keywords receive an already-scoped image selector.
Resource    ../browser.resource

*** Variables ***
${IMAGE_IS_LOADED}    (img) => Boolean((img.currentSrc || img.src) && img.complete && img.naturalWidth > 0)
${IMAGE_STATE}        (img) => ({ src: img.currentSrc || img.src, alt: img.alt, complete: img.complete, naturalWidth: img.naturalWidth })
# Product photography is 1080px square and served from the media CDN;
# placeholder pixels and fallback art are not.
${PRODUCT_MEDIA_URL}    ^https://media[.]btech[.]com/catalogs/
${MIN_IMAGE_WIDTH}      200

*** Keywords ***
Image Should Be Present
    [Arguments]    ${image_locator}    ${expected_alt}
    Wait For Elements State    ${image_locator}    visible    ${IMAGE_TIMEOUT}
    Get Attribute    ${image_locator}    alt    ==    ${expected_alt}
    Get Attribute    ${image_locator}    src    validate    bool(value)

Image Should Be Fully Loaded
    [Documentation]    Proves the browser fetched and decoded the image, not that it looks
    ...                correct. A visual check needs a stable baseline, which a journey that
    ...                picks its product at runtime does not have.
    [Arguments]    ${image_locator}    ${expected_alt}
    Scroll To Element    ${image_locator}
    Wait For Elements State    ${image_locator}    visible    ${IMAGE_TIMEOUT}
    Wait For Function    ${IMAGE_IS_LOADED}    selector=${image_locator}    timeout=${IMAGE_TIMEOUT}
    ${state}=    Evaluate JavaScript    ${image_locator}    ${IMAGE_STATE}
    Image State Should Be Loaded    ${state}    ${expected_alt}    ${PRODUCT_MEDIA_URL}    ${MIN_IMAGE_WIDTH}
