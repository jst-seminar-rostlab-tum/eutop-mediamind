# Adding a new subscription

To add a new subscription set the following values correctly for the new entry in the subscriptions table:
* **domain**: provide the domain of the newspaper's homepage. If the website is paywalled, it is recommended to directly provide the link of its login page
* **paywall**: make sure to set this column as true if the website is paywalled, the login won't execute otherwise
* **is_active**: the subscription will be ignored by the pipeline if this value is not set to true
* **login_config**: if needed, provide the json with the xpaths of all the necessary elements to complete the login (see LOGIN_SCRAPING documentation)
* **logout_config**: highly recommended to provide this config if login is done
* **encrypted_username**
* **encypted_password**
