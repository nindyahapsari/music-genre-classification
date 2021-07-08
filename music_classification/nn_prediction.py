import tensorflow as tf
import math
import numpy as np
import librosa

SAVED_MODEL_PATH = "nn_model.h5"
# NUM_SAMPLES_TO_CONSIDER = 22050 #1 sec
SAMPLE_RATE = 22050
TRACK_DURATION = 30 # measure in second
SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION


class _Genre_Classification_Prediction:
    model = None
    _mapping = [
        "classical",
        "hiphop",
        "pop",
        "rock"
    ]
    _instance = None

    


    def predict(self, file_path):
        # add a dimension to input data for sample - model.predict() expects a 4d array in this case
        # X = X[np.newaxis, ...] # array shape (1, 130, 13, 1)

        # extract MFCC
        MFCCs = self.preprocess(file_path, num_segments=10)

        # need 4 dimesional array to feed to the model for prediction ( #samples, #time steps, #coefficients, 1)
        MFCCs = MFCCs[np.newaxis, ..., np.newaxis]
        # print("MFCC:", MFCCs)

        # get the predicted label
        # perform prediction
        predictions = self.model.predict(MFCCs)
        # print(predictions)

        # get index with max value
        predicted_index = np.argmax(predictions)
        # print("predicted index: {}".format(predicted_index))
        predicted_genre = self._mapping[predicted_index]

        return predicted_genre

    def preprocess(self, file_path, num_mfcc=13, n_fft=2048, hop_length=512, num_segments=5):

        num_sample_per_segment = int(SAMPLES_PER_TRACK / num_segments)
        expected_num_mfcc_vector_per_segment = math.ceil(num_sample_per_segment / hop_length) # 1.2 -> 2

        signal, sample_rate = librosa.load(file_path)

        # if len(signal) >= NUM_SAMPLES_TO_CONSIDER:
            # ensure consistency of the length of the signal
            # signal = signal[:NUM_SAMPLES_TO_CONSIDER]
    
        for segment in range (num_segments):
            start_sample = num_sample_per_segment * segment #s=0 -> 0
            finish_sample = start_sample + num_sample_per_segment # s=0 -> num_samples_per_segment

            # extract MFCCs
            MFCCs = librosa.feature.mfcc(signal[start_sample:finish_sample], sample_rate, n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
            return MFCCs.T


def Genre_Classification_Prediction(): 
    if _Genre_Classification_Prediction._instance is None:
        _Genre_Classification_Prediction._instance = _Genre_Classification_Prediction()
        _Genre_Classification_Prediction.model = tf.keras.models.load_model(SAVED_MODEL_PATH)
    return _Genre_Classification_Prediction._instance


if __name__ == '__main__':

    # create 2 instances of the genre classification 
    gcp = Genre_Classification_Prediction()
    gcp1 = Genre_Classification_Prediction()

    # check that different instances of the genre classification point back to the same object (singleton)
    assert gcp is gcp1

    # make a prediction
    genre = gcp.predict("cnn_test/classical.wav")
    print("Predicted genre: {}".format(genre))

################### Predict function should go in another separated file ###########################
    # pick a sample to predict from the test set
    # x_to_predict = X_test[100]
    # y_to_predict = y_test[100]

    # predict sample
    #predict(model, x_to_predict, y_to_predict)
    ################################################
