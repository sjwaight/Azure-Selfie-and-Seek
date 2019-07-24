# Azure Selfie-and-Seek Game Play

This page describes how the game is played. Read about administering / running the games on the [admin page](admin.md).

## Enabling the game

It is recommended that when you aren't running the game that you disable the Logic Apps for registration and game play. If you have done this you should ensure you enable them prior to starting any event.

Additionally, you should also ensure you have the following correctly configured:

- A Person Group on Face API: create using the [Face API REST API](https://docs.microsoft.com/en-us/rest/api/cognitiveservices/face/persongroup/create) / docs and then configure in the admin portal of the game.
- The correct event name: this is displayed on the booth display static website so you should ensure you have the right event name to display!

## Player Registration

Once an admin has enabled the game, a player can register to play by tweeting a selfie to the designed Twitter account that will be used to run the game. The player must send a selfie and the hashtag #rego.

> **Note:** players should ensure this selfie includes only their face! Azure Cognitive Services is really good at face recognition, so even a small face in the background is enough to cause registration to fail.

See below for a sample registration tweet (we used the Twitter handle 'BitWhere' for our game play).

![Alt text](new-registration-sample.JPG?raw=true "Registration Sample Tweet")

Before a player can participate their registration must be confirmed on the admin web application. This is done to ensure people registering are physically present and that they have constented to participate in the game. See how to administrer the game on the [admin documentation page](admin.md).

## Playing the Game

Once an administrator uses the admin website to randomly select a regsitered player as the "hidden" player they can set the booth display to show the obfuscated picture of that person (see sample below).

![Alt text](displayed-image.jpg?raw=true "Hidden Player Booth Sample")

At this point all registered players must search for that person. A participant who thinks they have found the hidden player should take a picture of the person then tweet that picture to the same Twitter account they used to register including the hashtag #found.

This photograph can have any number of people in it as the gameplay Logic App will iterate over all faces to see if any of them is the "hidden" player.

![Alt text](winning-entry-sample.jpg?raw=true "Winning Entry Sample Tweet")

So how does everyone know when someone has won? The gameplay Logic App will mark all winning entries and a game adminstrator should use the admin web app to select the winning player (this could be automated but right now is not).
