*** Settings ***
Documentation    Shared technical imports for every resource that calls Browser keywords.
Variables    ../config.py
Library      Browser    timeout=${ACTION_TIMEOUT}
Library      Collections
Library      ../libraries/search.py
Library      ../libraries/cart.py
Library      ../libraries/images.py
