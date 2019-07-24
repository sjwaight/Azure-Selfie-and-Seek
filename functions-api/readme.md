# Azure Functions REST API

This folder contains an Azure Functions project that provides three simple REST endpoints that are required to run the [booth display](../booth-display).

- ActiveGame: returns the data that drives the active game booth display (basically the URL of the image to render for the 'hidden player')
- GameStatus: returns which mode the game is in - attractor, active game (no winner), winner.
- WinnerGame: returns the data that drives the winner game booth display that shows the original selfie of the 'hidden player', the winning picture, and the winning player's original selfie.

## Configuration

You require one custom application setting for these three Functions to work. This setting tells the three Functions where to read the game data from.

- GAMEDATA_STORAGE - A fully qualified Azure Storage connection string that points at the Storage Account containing your Table data.

Either manually deploy the above using the Azure Portal, or use the CLI '[az webapp config appsettings set](https://docs.microsoft.com/en-us/cli/azure/webapp/config/appsettings?view=azure-cli-latest#az-webapp-config-appsettings-set)' command to push up.

---
**NOTE**

You must allow * (or your specific host) in the CORS setting for the Function App, otherwise the API will not return data. Details on how to do this can be found on [the Microsoft Docs site](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings#cors).

---

## Deploying

You can use the Azure Functions extension for Visual Studio Code to deploy the Functions here to Azure. This is already well documented so go and [have a read](https://code.visualstudio.com/tutorials/functions-extension/deploy-app)!

It's also possible to deploy Functions using a centralised CI / CD platform like Azure DevOps, though this becomes more challenging when multiple solutions with multiple destinations are present in a single repository like this demo. If you want to do an Azure DevOps deployment you can consider moving solutions to Git Branches or to individual Git repositories.