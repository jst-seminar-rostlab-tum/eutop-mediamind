# MediaMind Newspaper Login

# Login

The login is done by using the following functions, using selenium:
* click_element: to click a regular html element
* click_shadow_element: to click an element inside a shadow root
* change_frame: to get inside and iframe and unlock interactivity with its elements
* scroll_to_element: necessary when the element is not visible on screen or it is blocked by another one
* insert_credential: to insert a value in an input field

The previous functions are used by the main function hardcoded_login, which makes the login process following the common login steps:
1. Get the subscription credentials, encrypted in the database
2. Get the login config from the subscription. This is a json containing all the neccesary xpaths
3. Initialize the website
4. Accept the cookies. This is important because if the cookies window is not removed it can end up blockig us from scraping. For this step we take into consideration the following possibilities:
- Handle iframes: the cookies window may be in an iframe, therefore we will have to change our driver's frame to interact with its elements
- Shadow host: in other cases the window is inside a shadow root, for that we use the click_shadow_element function, designed specifically for these cases
5. Remove notifications. Aafter accepting the cookies is common that a notifications/advertisement/etc window appears
6. Open login form, that is, navigate to the website's page with the input fields for the credentials
7. Submit login credentials, for this final step we follow these steps:
- Insert username
- Insert password
- Click submit button
- Click second submit button. In some websites first you have to submit the username, and then a new form opens for the password, for this reason it's necessary to store both buttons for this specific case

Most of the time a website won't require to follow all the previous steps to complete the login, therefore the login_config json will be different for each one. These are all the possible keys that the login config can have:
* shadow_host_cookies: CSS Selector of the shadow host that contains the shadow DOM content with the accept cookies element
* iframe_cookies: Xpath of the iframe that contains the accept cookies element
* cookies_button: - Xpath of the accept cookies element itself (use CSS Selector instead of Xpath only if this element is inside a shadow root)
* refuse_notifications: Xpath to refuse notifications, remove ads or any undesired window
* path_to_login_button: Xpath of the element that triggers/makes visible the element to open the login form
* login_button: Xpath of the element which opens the login form
* iframe_credentials: XPath of the iframe that contains the credential input fields
* user_input: XPath of the input field where the username/email is typed
* password_input: XPath of the input field for the password
* submit_button: XPath of the element that submits the credentials
* second_submit_button: XPath of the element that submits the credentials in two step login cases

Important notes:
* After exiting an iframe, you can see that we always use driver.switch_to.default_content(), this is highly important, since otherwise the driver will stay in the iframe's context and won't be able to interact with the website's elements
* The code cannot use xpaths to interact with elements inside a shadow root. To properly interact with them use CSS Selectors only in this case.
* The name of the keys of the login config json have to be always the same, since the code looks for those specific names to retrieve the xpaths.
* Code just executes a step if the xpaths to complete that step are in the login config json
* If keys are provided for an unexisting step in the website, the code won't break, the attempt will simply fail and a warning will logged

# Logout

If the login is done, it's highly recommended to do the logout as well before leaving the website, otherwise the sessions will remain open and at some point the session limit will be reached, blocking the login to the website. The same logic is repeated in the logout, and the same functions to interact with elements are used. The logout config is stored separately from the login config in the database.

The hardcoded_logout function follows this general process:
1. Go to the profile page, which usually contains the logout button
2. Change to the iframe containing the logout button, if any
3. Click the logout button

Therefore the possible keys for the logout config json are:
* profile_section
* iframe_logout
* logout_button

Just like the login config, these names must be kept, since the code looks specifically for them.

# LLM Approach

To avoid manual update of every broken subscription login config, we provide an automated LLM-based solution.

The process is the following:
1. Get the subscription's credentials
2. Set the number of attempts the LLM will have to complete the process (currently 8 in the code), that is, the number of calls we will make. In the worst case scenario at least four attempts will be needed (send the homepage, send the profile page, send the username form page, send the password form page)
3. Initialize the new login config json
4. Start first attempt (currently limited to 8)
5. Extract the page's html
6. Extract the html from iframes and shadow roots and merge it with the page's html
7. Clean the complete html (select the body, remove styles, scripts, SVG instructions)
8. Take a screenshot of the current page (has proven to give better results)
9. Send the html and the screenshot to the LLM, mentioning in the instructions all the elements that the login config json can have
10. Add the responses to the new login config json
11. Test the responses by following the general login process
12. Evaluate if the login was completed, for that four things must be true:
* The username was inserted
* The password was inserted
* The submit button was clicked
* An 200 OK response was captured by the driver just after clicking the submit button
13. If the login was not completed, another attempt is started
14. Whether the service succedeed or not, the date of the run is stored in the the database (llm_login_attempt). This date is used to limit the use of this service

Important notes:
* The login_config is updated in the database only if the login is completed successfully.
* Since an html can consist of thousands (in some cases more than one million) tokens, this approach can be expensive. For that reason, usage is limited to one use per subscription per week. This is done by registering the date of the latest attempt in the subscriptions table (llm_login_attempt)
