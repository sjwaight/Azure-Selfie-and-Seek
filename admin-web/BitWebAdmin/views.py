"""
Routes and views for the flask application.
"""
from . import app

# Import our confiugraiton items
import storage_config, aad_config, face_api_config

# Face API import and config
import cognitive_face

cognitive_face.Key.set(face_api_config.FACE_API_KEY)
cognitive_face.BaseUrl.set(face_api_config.FACE_API_HOST)

# Azure Table Storage import and config
from azure.storage.blob import BlockBlobService, ContentSettings
from azure.storage import CloudStorageAccount
from azure.storage.table import TableService, Entity, EntityProperty, EdmType

table_service = TableService(storage_config.STORAGE_ACCOUNT, storage_config.STORAGE_KEY)

# Setup Application Insights for telemetry and debugging
from applicationinsights import TelemetryClient
tc = TelemetryClient(app.config['APPINSIGHTS_INSTRUMENTATIONKEY'])

import operator
from PIL import Image, ImageDraw, ImageOps
import socket
import requests
import uuid
import adal
import jwt
import io
from io import BytesIO
import random
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import InputRequired
from forms_definitions import GameAdminForm, ConfirmUserForm, FindUserForm, EventAdminForm, GameModeForm
from datetime import datetime
from flask import render_template, request, json, session, redirect, url_for, Response, current_app

@app.route("/login")
def login():

    redirect_uri = '{}://{}/setupsession'.format(app.config['PREFERRED_URL_SCHEME'], request.host)

    auth_state = str(uuid.uuid4())
    session['state'] = auth_state
    authorization_url = aad_config.TEMPLATE_AUTHZ_URL.format(
        aad_config.TENANT,
        aad_config.CLIENT_ID,
        redirect_uri,
        auth_state,
        aad_config.RESOURCE)

    return redirect(authorization_url, code = 307)

@app.route("/setupsession")
def setupsession():

    # extract returned values from URL
    code = request.args['code']
    state = request.args['state']

    if state != session['state']:
        raise ValueError("State does not match")

    redirect_uri = '{}://{}/setupsession'.format(app.config['PREFERRED_URL_SCHEME'], request.host)

    # now request tokens
    auth_context = adal.AuthenticationContext(aad_config.AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, redirect_uri, aad_config.RESOURCE, aad_config.CLIENT_ID, aad_config.CLIENT_SECRET)

    # It is recommended to save this to a database when using a production app.
    session['access_token'] = token_response['accessToken']

    return redirect(url_for('home'))

@app.route('/')
@app.route('/home')
def home():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    return render_template(
        'index.html',
        title='Home Page',
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
    )

@app.route('/findplayer')
def findplayer():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    form = FindUserForm()

    return render_template(
        'findplayer.html',
        title='Find Player',
        form = form,
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
    )

@app.route('/confirmplayer', methods=['POST'])
def confirmplayer():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))
   
    form = ConfirmUserForm() 
    form.user_name = request.form['user_name']
    img_user = ""
    player_lookup_status = ""
    player_save_status = ""
   
    game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)

    if form.validate_on_submit():
           
        try:
            # Try and find the user registration for the player
            user_doc = table_service.get_entity(storage_config.PLAYER_TABLENAME, request.form['user_name'], game_config['activeevent'])

            # Update the registration to confirmed so player can play
            user_doc['confirmed'] = form.user_confirmed.data

            table_service.update_entity(storage_config.PLAYER_TABLENAME, user_doc)

            player_save_status = "Saved OK"

        except Exception as e:
            tc.track_exception(e)
            tc.flush()
                
            player_save_status = f"Unknown error saving user ({e})"

    else:

        # Try and find the user registration for the player and at least one valid Face API processed selfie

        try:
                 
            user_doc = table_service.get_entity(storage_config.PLAYER_TABLENAME, request.form['user_name'], game_config['activeevent'])
         
            # Set the checked state of the field based on true / false in table storage
            form.user_confirmed.checked = user_doc['confirmed']
           
        except Exception as e:
            tc.track_exception(e)
            tc.flush()          

        try:

            # If we found the user go ahead and try and find a valid Face image for them
            if player_lookup_status == "":

                images = list(table_service.query_entities(storage_config.PLAYER_IMG_TABLENAME, filter="faceid ne '' and PartitionKey eq '" + request.form['user_name'] + "'", num_results=1))

                # Set URL we send back to web page to view image
                img_user = images[0]['imgurl']
                
                # Add a flag to image entity so we know this was the one we saw and confirmed on (makes it easier to select later)
                images[0]['selected'] = True
                table_service.update_entity(storage_config.PLAYER_IMG_TABLENAME, images[0])

        except Exception:
            tc.track_exception()
            tc.flush()

    return render_template(
        'confirmplayer.html',
        title='Confirm Player',
        form=form,
        playerlookup=player_lookup_status,
        playersave=player_save_status,
        imgurl=img_user,
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
    )

@app.route('/trainmodel', methods=['GET'])
def trainmodel(): 

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    try:

        # Load game configuration so we know which Person Group to train
        game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)

        # Setup Azure Conginitive Service Face API and train group
        cognitive_face.person_group.train(game_config['persongroup'])
   
    except Exception as e:
            tc.track_exception(e)
            tc.flush()          

    return render_template(
        'trainmodel.html',
        title='Train Model',
        message='Training Model.',
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
    )

@app.route('/trainingstatus', methods=['GET'])
def trainingstatus():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return Response("Access Denied", 401)

    status = "error"
    
    try:

        # Load game configuration so we know which Person Group to train
        game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)
    
        status = cognitive_face.person_group.get_status(game_config['persongroup'])['status']

    except Exception as e:
            tc.track_exception(e)
            tc.flush()

    finally:

        return status
        

@app.route('/eventadmin', methods=['GET', 'POST'])
def eventadmin(): 

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    form = EventAdminForm()
    saved_status = ""

    game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)

    if form.validate_on_submit():

        try:
            game_config['activeevent'] = form.event_location.data
            game_config['persongroup'] = form.person_group.data
        
            table_service.update_entity(storage_config.GAME_CONFIG_TABLENAME, game_config)

            saved_status = "success"
        except:
            saved_status = "danger"

    else:

        form.event_location.data = game_config['activeevent']
        form.person_group.data = game_config['persongroup']

    return render_template(
        'eventadmin.html', 
        title='Event Admin',
        savedstatus=saved_status,
	    form = form,
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
        )

@app.route('/gameadmin', methods=['GET', 'POST'])
def gameadmin(): 

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    form = GameAdminForm()    
    form.game_round.choices = [(0,'None'),(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')]
    
    # Read game configuration
    game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)
    
    if form.validate_on_submit():
             
        if(int(form.game_round.data) != 0):

            try:

                # Select records for players only if they are 'confirmed' and have not previously been selected as the hidden character (byteround = 0)
                results = list(table_service.query_entities(storage_config.PLAYER_TABLENAME, filter="confirmed eq true and byteround eq 0", select="PartitionKey", num_results=1000))
     
                 # total available users 
                item_count = len(results)
                # select a random integer representing position in list to select
                user_to_select = random.randint(0,item_count-1)
                # select new Bit user from list - list consists of document ID
                new_bit_user = results[user_to_select]
                
                user_doc = table_service.get_entity(storage_config.PLAYER_TABLENAME, new_bit_user['PartitionKey'], game_config['activeevent'])              

                # Load the static Bit character image (should have an alpha background - PNG)
                bit_img_response = requests.get(storage_config.BIT_IMAGE_SAS_URL)
                bit_image = Image.open(BytesIO(bit_img_response.content))      

                ## Load one of the player's selfies
                images = list(table_service.query_entities(storage_config.PLAYER_IMG_TABLENAME, filter="selected eq true and PartitionKey eq '" + new_bit_user['PartitionKey'] + "'", num_results=1))

                player_img_url = images[0]['imgurl']

                face_id = images[0]['faceid']
                rect_top =int(images[0]['faceRectTop'].value)
                rect_left = int(images[0]['faceRectLeft'].value)
                rect_width = int(images[0]['faceRectWidth'].value)
                rect_height = int(images[0]['faceRectHeight'].value)
                rect_right = rect_left + rect_width
                rect_bottom = rect_top + rect_height

                player_img_response = requests.get(player_img_url)
                player_img = Image.open(BytesIO(player_img_response.content))

                ## Resize static Bit image to be smaller that selfie
                resized_bit_image = ImageOps.fit(image = bit_image, size = (rect_width, rect_height))
        
                ## Uncomment to draw a rectangle where the face rectangle has been determined.
                ##dr = ImageDraw.Draw(playerImage)
                ##dr.rectangle((rectLeft, rectTop, rectRight, rectBottom), outline="red")

                ## Paste Bit into the player's selfie, using alpha mask from Bit image.
                player_img.paste(im = resized_bit_image, box = (rect_left, rect_top, rect_right, rect_bottom), mask = resized_bit_image)

                ## Upload merged image to Blob storage so we can serve on big screen.        
                new_img_byte_array = io.BytesIO()
                player_img.save(new_img_byte_array,'JPEG')
                block_blob_service = BlockBlobService(account_name=storage_config.STORAGE_ACCOUNT, account_key=storage_config.STORAGE_KEY)
                block_blob_service.create_blob_from_bytes(container_name = storage_config.BIT_IMAGE_CONTAINER, blob_name = face_id +".jpg", blob = new_img_byte_array.getvalue(), content_settings=ContentSettings(content_type='image/jpeg'))
        
                bitly_user_handle = user_doc['PartitionKey']
                bitly_blob_url = 'https://' + storage_config.STORAGE_ACCOUNT + '.blob.core.windows.net/' + storage_config.BIT_IMAGE_CONTAINER + '/' + face_id + '.jpg'

                ######
                ## If images processed OK then write content to Cosmos

                ## Set the round ID to be the currently selected round.
                user_doc['byteround'].value = form.game_round.data
                ## Write document back to Cosmos
                table_service.update_entity(storage_config.PLAYER_TABLENAME, user_doc)

                # # Set the new game level and write game configuration to Cosmos
                game_config['activetier'].value = form.game_round.data
                game_config['bitimgurl'] = bitly_blob_url
                game_config['bitclearurl'] = player_img_url
                game_config['currentbit'] = bitly_user_handle
                game_config['currentpersonid'] = user_doc['personid']

                table_service.update_entity(storage_config.GAME_CONFIG_TABLENAME, game_config)

            except Exception as e:
                tc.track_exception(e)
                tc.flush()

            finally:  

                return render_template(
                    'saved.html',
                    title='Select a new Bit',
                    bitly=bitly_user_handle,
                    gameround=form.game_round.data,
                    bitlyurl=bitly_blob_url,
                    telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
                    )
      
        else:

            # load existing values into the form
            form.game_round.process_data(game_config['activetier'].value)
               
            return render_template(
                'gameadmin.html',
                title='Select a new Bit',
		        form = form,
                telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY'])

    else:

        # load existing values into the form
        form.game_round.process_data(game_config['activetier'].value)
               
        return render_template(
            'gameadmin.html',
            title='Select a new Bit',
		    form = form,
            telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
            )

@app.route('/winner', methods=['GET'])
def winner():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    form = GameAdminForm()    
    form.game_round.choices = [(0,'None'),(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')]
    
    if form.validate_on_submit():     
        # Did user select a round other than 'None'
        if(int(form.game_round.data) != 0):
            # If so, set that to be round to load data for
            game_round = form.game_round.data    
    else:

        # Read game configuration
        game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)    
        # load existing values into the form
        form.game_round.process_data(game_config['activetier'].value)            

    return render_template(
        'winner.html',
        title='Winner View',        
		form = form,
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
        )


@app.route('/displaymode', methods=['GET', 'POST'])
def displaymode():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return redirect(url_for('login'))

    form = GameModeForm()    
    
    # Read game configuration
    game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)    

    if form.validate_on_submit():     
        game_mode = form.game_mode.data    

        game_config['gamestatus'] = form.game_mode.data

        table_service.update_entity(storage_config.GAME_CONFIG_TABLENAME, game_config)

    else:

        # Read game configuration
        game_config = table_service.get_entity(storage_config.GAME_CONFIG_TABLENAME, storage_config.GAME_CONFIG_PARTITIONKEY, storage_config.GAME_CONFIG_ROWKEY)    
        # load existing values into the form
        form.game_mode.process_data(game_config['gamestatus']) 

    return render_template(
        'displaymode.html',
        title='Game Display Mode',        
        year=datetime.now().year,
		form = form,
        telemetrykey=app.config['APPINSIGHTS_INSTRUMENTATIONKEY']
        )


@app.route('/winnerstatus', methods=['GET'])
def winnerstatus():

    if aad_config.OAUTH_ENABLED and 'access_token' not in session:
        return Response("Access Denied", 401)

    try:
        game_round = int(request.args.get('round'))
    
        if(game_round != 0):

            winningEntries = list(table_service.query_entities(storage_config.PLAY_ATTEMPTS_TABLENAME, filter="status eq 'matched_bitly' and gamelevel eq " + str(game_round), select = "PartitionKey, postbody", num_results=1))

            return json.dumps(winningEntries)

    except Exception as e:
        tc.track_exception(e)
        tc.flush()

    return json.dumps(list())