# Player Registration and Game Engine

This folder contains the [Azure Logic Apps](https://docs.microsoft.com/en-us/azure/logic-apps/) that are used for player registration and as the actual game engine.

## Deploying

These Logic Apps can be deployed by executing the Deploy-LogicApp.ps1 PowerShell script contained in the matching Logic App Folder.

The deployment expects there to be an Azure Key Vault in your subscription that contains two secrets (gamefacekey, gamestoragekey) that are required at deployment time. The user deploying the Logic Apps must be able to read these secrets otherwise deployment will fail!

Before depoying you must update the parameters.json file for each Logic App and update the following values:

- YOUR_SUBSCRIPTION: The Azure Subscription which contains the Key Vault you wish to use.
- YOUR_RESOURCE_GROUP: The Resource Group in which the Key Vault resides.
- YOUR_KEY_VAULT: The name of your Key Vault.