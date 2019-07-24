# Game Admin Website

This folder contains a Python 3 Flask web application that is used to administer the Selfie-and-Seek game.

## Deploying

This is a standard Python 3 Flask web application so can be deployed anywhere, but for the purposes of this solution we will be deploying it to Web Apps running on [Azure App Service on Linux](https://docs.microsoft.com/en-us/azure/app-service/containers/app-service-linux-intro).

### Create an App Service on Linux Web App

You can use the following script to deploy an empty Web App on Azure that you can deploy the contents of this folder to.

Note: you might want to consider changing the "location" and "sku" values to match your needs.

```bash
#!/bin/bash

# Based on: https://docs.microsoft.com/en-us/azure/app-service/scripts/cli-linux-docker-aspnetcore#sample-script

# Variables
appName=$1
appPlanName="${appName}plan"
resGroupName=$2
location="WestUS2"

# Create a Resource Group
az group create --name $resGroupName --location $location

# Create an App Service Plan
az appservice plan create --name $appPlanName --resource-group $resGroupName --location $location --is-linux --sku B1

# Create a Web App
az webapp create --name $appName --plan $appPlanName --resource-group $resGroupName --runtime "python|3.6"

# Copy the result of the following command into a browser to see the web app.
echo http://$appName.azurewebsites.net
```

The easiest way to do this is to use Azure Cloud Shell and then run the following commands:

```bash
curl https://gist.githubusercontent.com/sjwaight/a105617a766717fda831df70373d92c0/raw/f74ba54262b36dd0d180827f4a4805cb9e3df3e6/createlinuxappservice.sh -o createlinuxappservice.sh
chmod 755 createlinuxappservice.sh
./createlinuxappservice.sh YOUR_WEB_APP YOUR_RESOURCE_GROUP_NAME
```
### Write App Settings into Azure

**Note:** in a future update this will be changed to use [Managed Service Identities](https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity) (MSI) when they become generally available for Linux App Services.

Modify the values for the following fields in the [appsettings.json](../deployment/appsettings.json) file in this repository 

**Note:** if an item is not listed below you do not need to change its value in the file.

- FLASK_KEY: a random string used at runtime to guard against [CSRF attacks in Flask WTForms](https://flask-wtf.readthedocs.io/en/stable/csrf.html).
- APPINSIGHTS_INSTRUMENTATIONKEY: a GUID that represents the [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) instance against which you wish to log telemetry.
- FACE_API_KEY: the [Azure Cognitive Servies Face API](https://docs.microsoft.com/en-au/azure/cognitive-services/face/overview) key you generated when setting up the project.
- FACE_API_HOST: the Azure Cognitive Services Face API endpoint against which all calls we be sent.
- STORAGE_ACCOUNT: the Azure Storage account which contains the [Table Storage](https://azure.microsoft.com/en-au/services/storage/tables/) you wish to use for the backend of the game.
- STORAGE_KEY: the key you wish to use to access the STORAGE_ACCOUNT.
- BIT_IMAGE_CONTAINER: the Azure Blob Storage container you wish to use when generating and serving your "hidden" player image.
- BIT_IMAGE_SAS_URL: the fully qualified SAS URL for the image you wish to use to hide the face of the person who is selected as your "hidden" player.
- OAUTH_ENABLED: if 'True' then require users to login (the remaining settings are then required); if 'False' then admin website is public (remaining settings are not required in this case).
- AADTENANT: the Azure AD tenant which you wish to use for authentication (and against which this app has been registered).
- CLIENT_ID: the Client / Application ID of your application in Azure AD.
- CLIENT_SECRET: the Client Secret generated / entered when you registered your application in Azure AD.

Once you have updated the values you can then deploy it to your configured Web App using the command as follows.

**Note:** do not commit the appsettings.json file to source control!

```bash
az webapp config appsettings set -g MyResourceGroup -n MyUniqueApp --settings @appsettings.json
```

### Configure Deployments directly from GitHub

If you fork this repository you can configure App Service so it will automatically deploy updated items on push. Rather than document here you can view the steps on [Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/deploy-continuous-deployment#deploy-continuously-from-github). On the second step of the setup you can select "App Service Kudu build server" as your Build Provider and then select the correct 