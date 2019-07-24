# Azure Selfie and Seek Administration

This page covers how you can run a Selfie and Seek game at an event using the included admin web application. If you are looking for how to play the game as registered player you should [read the main page](README.md) of this folder.

The admin website provides the following capabilities:

- Confirming players: ensuring people who are playing are at the event or have consented to participate.
- Selecting a new 'hidden' player: this starts a new game.
- Find a winner: search for submitted entries to find out if someone won.
- Control booth display mode: show a different screen at the booth.
- Configre the event details: set event display name and Face API person group to use.
- Manually trigger training of Face API: optional and Face API generally works without the need to use.

## Access the admin website

If the website has been deploye with Azure AD integration setup you will pass through the standard OAuth-based login experience before being returned to the main page of the admin website which is shown below.

![Alt text](admin-home.jpg?raw=true "Admin website home")

## Registering / confirming players

By default all players who send a selfie to register to play must be manually confirmed using the `Confirm players` page. When you click on the button on the home page you will be presented with a search box.

Enter the player's Twitter handle (the search is case sensitive) and if the player's details have been captured successfully then they will be rendered as show below.

Check the 'Confirm Player' checkbox and then click the `Confirm This Player!` button. The page will refresh and the player is now included in the pool of people playing the game. You can return to the search screen to confirm another person by clicking on the `Confirm Another Player` button.

> Notes:
> 1. There is room for improvement in this feature - it will not be very descriptive when a player cannot be found. Ideally an update to make the search case insensitive would be a good fix :star:
> 2. The Logic App only reads Twitter once every 60 seconds (this is a limit placed on the API by Twitter) so it could also be that a player's registration hasn't yet been accepted.
> 3. If all else fails crack open Azure Storage Explorer and look at the contents of the Table Storage logs.

![Alt text](admin-confirm-player.jpg?raw=true "Confirming a player")

## Start a new game round

The game logic supports the ability to play up to 6 'rounds' where a new person will be selected as the player to find for each round. Before you can start a game round a player must be chosen at random by opening the `Select hidden player` page (shown as `Select a new Bit` on the screenshots here).

The currently active game round will be selected in the drop-down (or none if you haven't played yet).

Change the drop-down to a new round (5 is shown below) and then click the `Choose Now!` button.

![Alt text](admin-select-bit-1.jpg?raw=true "Select new hidden player")

The admin web logic will select a regiseterd player at random and then generate an obfuscated image of the player based on their provided selfie. The page will refresh and you will be shown the obfuscated image and the Twitter handle of the selected player.

![Alt text](admin-select-bit-2.jpg?raw=true "Selected hidden player")

Click on the `Change Game Mode` button to go to the page that allows you to control the booth display, or, if you don't want to make the game active yet then click `Home`.

## Confirming a winner

Multiple people may find the hidden player and submit entries. The `View Winner` page allows administrators to quickly identify who has found the hidden person.

> Note: this page is very basic and does not render the submitted image - you can check the image by loading it in a browser (or in Twitter) if that is required.

Open the page, select the round you want to find the winner for and then click the `Start listening` button. The page will check for winners every 60 seconds, and when it finds entries they will be rendered in a list. You can leave it running if you wish and it will continue to add entries as they arrive.

![Alt text](admin-found-bit.jpg?raw=true "Found Bit")

## Set event details

This screen allows you to set the event name displayed on the booth and also determine which Face API person group will be used for the event. It's a good idea to set a new person group per event you plan to run the game at.

![Alt text](admin-event-details.jpg?raw=true "Event Details")
