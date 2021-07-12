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

app = Flask(__name__)

# this for redirecting stuff
state = ''.join(
    secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
)

user_id = "BQAIMEjmZGoSF2DWyrYOGaVerhX3-M-ZJ_pyn3dpVtjq2ZQ1bB1a_yVz323tMb6Rv9t9As_xdBu41QQqfwx3nwPAyCm4qry2Nid_H2cIzvrH_VE8wqO6w4Hgbr5lS-l25uc-z6t6E8ap3vvpQevjj9PwA8OuC911I7cc9wF-uKb4D2jcPRg432aKsaP_hA"

# access_token_expired = "BQCg0aoO01sEV8fz9UAH1zZXxl5b8aTjUUrfLztzch5fZ3sOxoIwoHmOnsXz1gRYUS1xmzR_CesPY1L90WJvNDEdUFAXvdlHtwYrdg4VMhIM79kuQQ1c0tC_Xa499D8esDJhKnGOLgaC1f3gemDVmLD_qHfzMJ_dy2UPY8PsLuOvxda2y_Y"



################################### END POINTS ###############################################
end_point_url = "https://api.spotify.com/v1/recommendations?"
auth_url = "https://accounts.spotify.com/authorize?"
token_url = "https://accounts.spotify.com/api/token?"
########################################################################################

client_id="4aff65a65ed246e2a1e5ac032b1d0ba8"
client_secret="6258cec6e50c47eb803e75c9b20bfedd"
redirect_uri = "http://127.0.0.1:5000/auth"
#redirect_uri=url_for('authorize', _external=True)
scope="playlist-modify-private"
code = "AQDKYTYHxcsahFx7l3R3u5VjUAAG_7YuwP7W2NAQ2mm6OvbZ7zWsQL1GiDdllKJT-Lxe1pkdJcIeoFBLZUvLTnarsQvpp2Gxr3GXvp7upcriHwjENTapC3OWzqyX10bky8u9r0XUPurpsIS8SFSzQIWIAxZ1eWdIg9LtCnbD-bpXnFWPfc3UegogRnfBePuscROhHpnIeQ"

encoded_client_secret = "NGFmZjY1YTY1ZWQyNDZlMmExZTVhYzAzMmIxZDBiYTg6NjI1OGNlYzZlNTBjNDdlYjgwM2U3NWM5YjIwYmZlZGQ="

credent_data = {
    'grant_type' : 'client_credentials'
}

@app.route("/", methods=['POST', 'GET'])
# @app.route("/")
def index():
    if request.method == "POST":
        predicted_genre = prediction()
        return render_template('index.html', result_prediction=predicted_genre)
    else:
        return render_template('index.html')


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
        print("result prediction:", result_prediction)
        return result_prediction

###############################################################################################
# NEXT STEP FOR PLAYLIST:
# 1. created playlist based on the genre. make sure the list changes, new recommendations
# 2. option for the playlist e.g danceability, music similar to certain artist, etc collected from input value 
# 3. playlist generator should not be in different page, it should be in the same page with genre classification which index page
###############################################################################################

@app.route("/playlist")
def playlist():

#     auth_code = get_auth_code()
    # token_res = get_token()
    # # acc_token = token_res.get('access_token')
    # print("REF TOKEN:", token_res)



    # filter
    limit=13
    market="US"
    seed_genres="pop"
    target_danceability=0.3
    uris=[]
    created_playlist=[]
    # seed_tracks='55SfSsxneljXOk5S3NVZIW'
    static_acc_token = "BQB5A3Zl4y2L0wfYlbOKAXPFJ9c5iCkBGD1G92mNi-C-3g-AMXLUeV1j2v7a_W8nnxEAvk9p4SCeKk-A_lLYOiv3V0RHwlcM6jH1Sjzz5uJim5fQynAEt-VKSk4EO0mRa-UZtsOJNWeH0ccEQ7gQkTNheEVTZGBut0WeAOdptVkwIVwZd5A"
   
    query = f'{end_point_url}limit={limit}&market={market}&seed_genres={seed_genres}&target_danceability={target_danceability}'

    response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": f"Bearer {static_acc_token}"})
    json_response = response.json()

    if response.status_code == 200:
        for i, j in enumerate(json_response['tracks']):
            uris.append(j['uri'])
            # print(f"\"{i['name']}\" by {i['artists'][0]['name']}")
            print(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
            created_playlist.append(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
            # return json.dumps(json_response['tracks'])
                        # return json_response['error']['message']
    else:
        print("Error message . {}".format(json_response['error']['message']))




    ################Creating Empty Playlist##########################

    data_playlist = json.dumps({
                'name' : 'New playlist generate using python and AI',
                'description' : 'First programmatic playlist',
                'public' : False
    })

    new_empt_playlist_url = f"https://api.spotify.com/v1/users/11136885927/playlists?"
    res_playlist = requests.post(new_empt_playlist_url, data=data_playlist, headers={"Content-Type": "application/json", "Authorization": f"Bearer {static_acc_token}"})
    print("RES_PLAYLIST:", res_playlist.json())
    playlist_url = res_playlist.json()['external_urls']['spotify']
    print(res_playlist.status_code)

    ########## Filling the empty playlist #################################
    playlist_res = res_playlist.json()
    playlist_id = playlist_res.get('id')
    print("playlist ID:", playlist_id)
    fill_playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?"
    data_fill_playlist = json.dumps({ "uris" : uris })
    print("data_fill_playlist:", data_fill_playlist)
    res_playlist_fill = requests.post(fill_playlist_url, data=data_fill_playlist, headers={"Content-Type": "application/json", "Authorization": f"Bearer {static_acc_token}"})
    print("res playlist:", res_playlist_fill.json())

    # ####### Print the playlist Url ###############
    print(f'Your Playlist is ready at {playlist_url}')

    #return statement should be outside loop area
    return "this have to out from the loop"                

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
    # cred_code = credentials_code()
    # print("CREDENTIALS_CODE: ", cred_code['access_token'])
    # token = cred_code['access_token']
    # return token
    
def req_new_token():
    data={'grant_type' : 'refresh_token', 'refresh_token': 'AQDWINzVeg5MhzgcQGSMVTs9rTX-h0AY1wnVl6XsiBgfQ3b51FNk92bHyfV1vhDbYOCmRrtrnOzZ7bqgk1u7FONMuD0K3a4bxbszbAmA5MAGRgTqj3tghRWt9QhMWXfoc10'}
    response = requests.post(token_url, data=data, headers={'Authorization': f"{encoded__client_secret}"})
    json_res = response.json()
    print("refrsh func", json_res)
    
def get_token():
    # for access_token and refresh_token
    res_data = request.args.get('code')
    print("res_data", res_data)
    data = {
        'grant_type' : 'authorization_code',
        'code' : res_data,
        'redirect_uri' : redirect_uri
    }

   #  auth_data = {
            # 'client_id': client_id,
            # 'response_type': 'code',
            # 'redirect_uri' : redirect_uri
            # 'scope' : scope
    # }

    # query = f"{token_url}grant_type={token}&code={code}&redirect_uri={redirect_url}"

    response = requests.post(token_url, data=data, headers={"Authorization": f"Basic {encoded_client_secret}"})
    json_response=response.json()
    print("JSON RESPONSE:", json_response)
    refresh_token = json_response.get('refresh_token')
    print("REFRESH TOKEN: ", refresh_token)
    #print("THE REQUEST FROM TOKEN FUNCT:", json_response['refresh_token'])
    return refresh_token


def get_auth_code():
# for new auth_code
    auth_response = make_response(redirect("https://accounts.spotify.com/authorize?client_id=4aff65a65ed246e2a1e5ac032b1d0ba8&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauth&scope=playlist-modify-private"))
    auth_response.set_cookie('spotify_auth_state', state)
    res_data = request.args.get('code')
    print("the get response:", res_data, auth_response.status_code)
    return auth_response 



def credentials_code():
            credent_response = requests.post(token_url, data=credent_data, headers={'Authorization' : f'Basic {encoded_client_secret}'})
            if credent_response.status_code == 200:
                print("STATUS_CODE 200 success!")
                cre_json_res = credent_response.json()
                print("credentials access token: ", cre_json_res)
                return cre_json_res
            else :
                error_status = credent_response.status_code
                print(error_status)


if __name__ == '__main__':
    app.run(debug=True)
