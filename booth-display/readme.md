# Booth Display Website

The contents of this folder are a simple static website that can be shown on a screen at a booth to show the status of the current Selfie-and-Seek game.

For our setup we used the [Static website feature](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website) of Azure Storage to host this site.

In order for the website to be fully functional you must have deployed the [Azure Functions API](../functions-api/readme.md) and have configured items in this solution for it to work on deployment. These configurations items are detailed later in this readme.

The web page that is displayed at any given time is driven by a game administrator changing the display mode in the [Game Admin Website](../admin-web/readme.md). The JavaScript in the Booth Display Website will poll for changes to the game status every 60 seconds.

## Configuration

Change the following placeholders in the three HTML files in this project before you deploy them to the storage account:

- YOUR-FUNCTIONS-API: change the Function App name where the API endpoints are deployed.
- FUNC-API-KEY: create a new [Function App Host Key](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook#webhooks-and-keys) and use this to secure the API endpoint (*don't* use the master or _default key)
- YOUR_INDEX_LINK: put the full public URL that people can open to view the index.html page for your static website - this should contain 'how to play' instructions.
- YOURTWITTER: replace with your selected Twitter handle (the one you have integrated with the Logic Apps) - this is a simple way to show the thread from the account.

## Display modes

Note: we have not included the 'Bit' character image in this solution.

### Attractor mode

This is used when you have no running games but would like to show something on a screen to let people know they can register.

![Attractor Mode](../docs/booth-display-attractor.png?raw=true "Attractor Mode")

### Active Game - No Winner mode

Once the administrator has selected a new hidden player you can show this screen which will render the obfuscated picture of the player to find, along with a Twitter embed of your selected Twitter game account. A sample is shown below.

![Active Game - No Winner](../docs/booth-display-active-game.png?raw=true "Active Game - No Winner")

### Active Game - Winner! mode

When a winner has been found the adminstrator can switch the display to this mode and it will show the hidden player's original selfie ("Bit" in our sample below), the picture the winner posted, along with the winner's selfie. A sample is shown below.

![Winner!](../docs/booth-display-winner.png?raw=true "Winner!")
