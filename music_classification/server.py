from flask import Flask, render_template, request, redirect
from nn_prediction import Genre_Classification_Prediction 
import random
import os


app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
