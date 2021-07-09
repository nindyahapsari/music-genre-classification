from flask import Flask, render_template, request, redirect
from nn_prediction import Genre_Classification_Prediction 
import random
import os
import requests
import json

app = Flask(__name__)

end_point_url = "https://api.spotify.com/v1/recommendations?"

token = "BQC_iLlSZOY4rlKjhUxUUXy8ZILfXqD3m3RBbGUJZY8qW0mzNliNo0ZX7ykIoNw2u5doVuRT5juFq4yduAbyReSefoBvoDZEKyMDnDk5EtajHwYVkMKxwQLLBrvB6BbWgKaw9bfRxP0DsUwiCyKRoTdtVhmpJzYFEskumzXlj89WZCp1AcYQpf3zNaHQ3Q"

user_id = "BQAIMEjmZGoSF2DWyrYOGaVerhX3-M-ZJ_pyn3dpVtjq2ZQ1bB1a_yVz323tMb6Rv9t9As_xdBu41QQqfwx3nwPAyCm4qry2Nid_H2cIzvrH_VE8wqO6w4Hgbr5lS-l25uc-z6t6E8ap3vvpQevjj9PwA8OuC911I7cc9wF-uKb4D2jcPRg432aKsaP_hA"

@app.route("/", methods=['POST', 'GET'])
# @app.route("/")
def prediction():
    if request.method == "POST":
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

        return render_template('index.html', result_prediction=result_prediction)

    else:
        return render_template('index.html')



@app.route("/playlist")
def playlist():
    # filter
    limit=13
    market="US"
    seed_genres="electronic"
    target_danceability=0.9
    uris=[]
    created_playlist=[]
    # seed_tracks='55SfSsxneljXOk5S3NVZIW'

    query = f'{end_point_url}limit={limit}&market={market}&seed_genres={seed_genres}&target_danceability={target_danceability}'
    # query += f'&seed_tracks={seed_tracks}'

    response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})

    json_response = response.json()
    # print(json_response)

    for i, j in enumerate(json_response['tracks']):
        # print(i)
        uris.append(j['uri'])
        # created_playlist.append(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
        print(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")


    # return json.dumps(created_playlist)
    return "playlist created look at console"

# next step: created playlist based on the genre. make sure the list changes, new recommendations


if __name__ == '__main__':
    app.run(debug=True)
