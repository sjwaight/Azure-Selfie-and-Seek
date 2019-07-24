# Azure Selfie-and-Seek Demo Game

This repository holds the various components that make up a Twitter-based game that uses [Azure's Cognitive Services Face API](https://docs.microsoft.com/en-us/azure/cognitive-services/face/) and [Azure Logic Apps](https://docs.microsoft.com/en-au/azure/logic-apps/) to let players attempt to find the one other player who is chosen at random as the "hidden" player.

The solution was used extensively during 2018 at a range of developer events in Australia under the banner of
"Where's Bit".

There is a [separate page](docs/) covering how the game works and a dedicated page for [how to administer the game](docs/admin.md).

The components that make up the overall solution are:

- A Twitter account: required to accept registrations and receive entries attempting to win.
- An image with alpha transparency: this is used to obfuscate the 'hidden' player during game play (this image must be uploaded into an Azure Blob Storage container and is referenced in the Python web admin codebase via `BIT_IMAGE_SAS_URL`).
- [Two Logic Apps](logic-apps/): one for player registration and one for game play.
- [A Python Flask Web App](admin-web/): used for administration of the game.
- [A Static Website](booth-display/): used to display the status of the game during game play.
- [A C# .Net Core Function API](functions-api/): provides the REST API that drives the Static Website display.
- [An ARM template](deployment/ARM-Template/): used to deploy the core platform features required to host the solution.
- An Azure Storage Account: used for Table Storage for game and player data, along with Blob Storage which is used for temporary image storage.
- Azure AD directory: used to protect the admin website (this is optional and can be commented out in the admin website if you don't want to use it).
- Azure Application Insights: captures runtime exception information from the admin web application.

Players who want to play the game only need to have a public Twitter account and be prepared to post a selfie.

## Manual setup components

You will need to configure the following items manually as they cannot be automated as part of the ARM deployment.

### Azure Table Storage

At time of publication you can't create Table Storage using ARM templates. The following Azure CLI commands will help you setup the required tables and data. You can use Azure Cloud Shell to run them.

```bash
# Note: a storage account is created with the ARM template - make sure to copy the account name and key from the Portal.

# Create Tables - ensure they are all in the same Storage Account
az storage table create --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY --name gameconfig
az storage table create --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY --name playerlist
az storage table create --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY--name playlogs
az storage table create --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY --name regologs
az storage table create --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY --name regourls

# Insert Config into 'gameconfig' table - update to match your configuration as required.

az storage entity insert --account-name YOUR_STORAGE_ACCOUNT --account-key YOUR_STORAGE_KEY --table-name gameconfig --entity PartitionKey=config RowKey=bit ActiveEvent='Your Event' ActiveTier=0 BitClearUrl='' BitImgUrl='' CurrentBit='' CurrentWinner='' GameStatus=pending PersonGroup=placeholder WinnerImgUrl='' WinnerSubmission=''

```

### Azure Active Directory

There are two components that require [Azure Active Directory](https://docs.microsoft.com/en-au/azure/active-directory/develop/index) (Azure AD):

1. Azure Logic Apps deployments using Key Vault: this is enabled via use of a [Service Principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals).

2. The Python Flask admin application uses [Azure Active Directory](https://docs.microsoft.com/en-au/azure/active-directory/develop/index) (Azure AD) for the user identity for admin access (players are *not required* to register in Azure AD to play). If you have an existing Azure AD tenant you can simply create a new Web App registration and update the appropriate settings the Flask Web App. Alternatively you can manually create a new tenant (basic tenants are free) and register the Web App in that instead.

### Logic App Connectors

The Logic Apps require [Connectors](https://docs.microsoft.com/en-us/azure/connectors/apis-list) in order to listen to the Twitter feed, call Face API and to use Azure Storage. These items will change per deployment so you'll have to set them up manually.

### Help!

If you get stuck getting this all up and running feel free to hit me up on Twitter [@simonwaight](https://twitter.com/simonwaight).
