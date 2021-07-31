from flask import Flask, render_template, request, redirect, url_for, session, make_response
from nn_prediction import Genre_Classification_Prediction 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import os
import requests
import json
import secrets
import string
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

# this for redirecting stuff
state = ''.join(
    secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
)

user_id = os.getenv("USER_ID") 

################################### END POINTS ###############################################
end_point_url = "https://api.spotify.com/v1/recommendations?"
auth_url = "https://accounts.spotify.com/authorize?"
token_url = "https://accounts.spotify.com/api/token?"
########################################################################################

client_id= os.getenv("CLIENT_ID")
client_secret= os.getenv("CLIENT_SECRET")
redirect_uri = "http://127.0.0.1:5000/auth"
#redirect_uri=url_for('authorize', _external=True)
scope="playlist-modify-private"
code = os.getenv("CODE")
refresh_token = os.getenv("REFRESH_TOKEN") 
encoded_client_secret = os.getenv("ENCODED_CLIENT_SECRET")

predicted_genre_nn =""

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/result", methods=['POST'])
def result():
    predicted_genre = prediction()
    predicted_genre_nn = predicted_genre

    if predicted_genre_nn != "":
        playlist_id = playlist(predicted_genre_nn)
        print("playlist-id:", playlist_id)
    else:
        print("prediction result not yet assigned")

    # pack_result = [predicted_genre, playlist_url]

    return redirect(f'/finalresult/{predicted_genre}/{playlist_id}')

@app.route("/finalresult/<predicted_genre>/<playlist_id>")
def finalresult(predicted_genre, playlist_id):
    print("result:", {predicted_genre}, "url:", {playlist_id})
    playlist_url_emb=f"https://open.spotify.com/embed/playlist/{playlist_id}"

    return render_template('result.html', predicted_genre=predicted_genre, playlist_url=playlist_url_emb) 
    
    




def prediction():
     # get audio file and save
     audio_file = request.files["audioFile"]
     file_name = str(random.randint(0, 100000))
     audio_file.save(file_name)
     print ("Audio file:", audio_file)

     # instantiate the singleton to get prediction
     gcp = Genre_Classification_Prediction()
     predicted_genre = gcp.predict(file_name)

     # we dont need the file anymore, delete the file
     os.remove(file_name)

     # the result from the prediction
     result_prediction = predicted_genre
     predicted_genre_nn = result_prediction
     print("PREDICTED GENRE:", predicted_genre)
     return result_prediction



###############################################################################################
# NEXT STEP FOR PLAYLIST:
# 1. created playlist based on the genre. make sure the list changes, new recommendations
# 2. option for the playlist e.g danceability, music similar to certain artist, etc collected from input value 
# 3. playlist generator should not be in different page, it should be in the same page with genre classification which index page
###############################################################################################

# @app.route("/playlist")
def playlist(genre_predicted):
    # filter
    limit=request.form['numSongs'] 
    market="US"
    target_danceability=request.form['danceability']
    uris=[]
    created_playlist=[]
    # seed_tracks='55SfSsxneljXOk5S3NVZIW'

    if genre_predicted  != "":
        if genre_predicted == "hiphop":
            seed_genres = "hip-hop"
        else:
            seed_genres=genre_predicted
        print("seed_genres", seed_genres)
    else:
        print("variable not assign")

    static_acc_token = os.getenv("STATIC_ACC_TOKEN")
    static_acc_token = static_acc_token
    new_access_token = req_new_token()
    # print("NEW ACCESS TOKEN:", new_access_token)

    query = f'{end_point_url}limit={limit}&market={market}&seed_genres={seed_genres}&target_danceability={target_danceability}'

    response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": f"Bearer {static_acc_token}"})
    json_response = response.json()

    if (json_response['error']['message'] == "The access token expired" and response.status_code == 401):
        print("Trying the request again, Error message:{}".format(json_response['error']['message']))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": f"Bearer {new_access_token}"})
        json_response = response.json()
        # print("response:", response.status_code, "json_response:", json_response)
        for i, j in enumerate(json_response['tracks']):
            uris.append(j['uri'])
            print(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
            created_playlist.append(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")

    else:
        for i, j in enumerate(json_response['tracks']):
            uris.append(j['uri'])
            print(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
            created_playlist.append(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")





    ################Creating Empty Playlist##########################

    data_playlist = json.dumps({
                'name' : 'New playlist generate using python and AI',
                'description' : 'First programmatic playlist',
                'public' : False
    })

    new_empt_playlist_url = f"https://api.spotify.com/v1/users/11136885927/playlists?"
    res_playlist = requests.post(new_empt_playlist_url, data=data_playlist, headers={"Content-Type": "application/json", "Authorization": f"Bearer {new_access_token}"})
    # print("RES_PLAYLIST:", res_playlist.json())
    playlist_url = res_playlist.json()['external_urls']['spotify']
    print(res_playlist.status_code)

    ########## Filling the empty playlist #################################
    playlist_res = res_playlist.json()
    playlist_id = playlist_res.get('id')
    # print("playlist ID:", playlist_id)
    fill_playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?"
    data_fill_playlist = json.dumps({ "uris" : uris })
    # print("data_fill_playlist:", data_fill_playlist)
    res_playlist_fill = requests.post(fill_playlist_url, data=data_fill_playlist, headers={"Content-Type": "application/json", "Authorization": f"Bearer {new_access_token}"})
    # print("res playlist:", res_playlist_fill.json())

    ######## Print the playlist Url ###############
    print(f'Your Playlist is ready at {playlist_url}')
    playlist_url2 = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    print(f'Your Embed Playlist is ready at {playlist_url2}')

    #return statement should be outside loop area
    return playlist_id








####################################################################################################
# STEPS FOR AUTH TOKEN/ACCESS TOKEN:
# need to get the spotify auth refresh token:
# 1. generate the auth access token and use it for 1 hour/ 60 minutes
# 2. check if the token is expired, if yes, generate a new access token by making POST request with grant_type=refresh code, OR reassign access_token value from credential_authorization (which not including the refresh token, and should be no login required)
# 3. return the value to the variable for the acces token and make it global
# 4. everything should be in one place and dont forget to clean the code
# 5. create a separate func for access token, refresh token
#
########################################################################################################

@app.route("/auth")
def auth_token():
    auth_code = get_auth_code()
    get_token()
    return auth_code


# put refresh token in env file
def req_new_token():
    data={
        'grant_type' : 'refresh_token', 
        'refresh_token' : refresh_token 
    }
    response = requests.post(token_url, data=data, headers={'Authorization': f"Basic {encoded_client_secret}"})
    json_res = response.json()
    refresh_access_token = json_res['access_token']
    print("REFRESH ACCESS TOKEN:", refresh_access_token)
    return refresh_access_token


def get_token():
    # for access_token and refresh_token
    res_data = request.args.get('code')
    print("res_data", res_data)
    data = {
        'grant_type' : 'authorization_code',
        'code' : res_data,
        'redirect_uri' : redirect_uri
    }

    # query = f"{token_url}grant_type={token}&code={code}&redirect_uri={redirect_url}"

    response = requests.post(token_url, data=data, headers={"Authorization": f"Basic {encoded_client_secret}"})
    json_response=response.json()
    refresh_token = json_response.get('refresh_token')
    return refresh_token


def get_auth_code():
    # url encoded /auth: http%3A%2F%2F127.0.0.1%3A5000%2Fauth
    # for new auth_code
    auth_response = make_response(redirect("https://accounts.spotify.com/authorize?client_id=4aff65a65ed246e2a1e5ac032b1d0ba8&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauth&scope=playlist-modify-private"))
    auth_response.set_cookie('spotify_auth_state', state)
    res_data = request.args.get('code')
    print("the get response:", res_data, auth_response.status_code)
    return auth_response 





if __name__ == '__main__':
    app.run(debug=True)
