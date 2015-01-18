Teksavvy Usage
==============

This script can be used to obtain Teksavvy usage data for an account,
given the account's API key.

In order to successfully use this script, you must first do three things:
* Get a teksavvy account
  Note that you must create this account manually.
  Teksavvy does not create this account for you when you sign up with them.
  https://myaccount.teksavvy.com/account/register
* Create an API key for that account
  https://myaccount.teksavvy.com/ApiKey/ApiKeyManagement
* Add the API key to the api_keys.ini file
  Just run the script and you should receive an appropriate error message
  Do not quote your API key.



Daily Notifications
===================

If you are worried about going over your monthly limit I suggest adding the 
following lines to your crontab:

::
   # This tells cron which display to use (required for notify-send)
   DISPLAY=:0

   0 1 * * * /usr/bin/python ABSOLUTE_PATH_TO_DIRECTORY_WHERE_USAGE_SCRIPT_IS_LOCATED/teksavvy_usage.py --notify-current

This will cause the *teksavvy_usage.py* script to be run every day at 1am.
