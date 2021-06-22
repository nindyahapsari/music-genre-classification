import json
import numpy as np
from sklearn.model_selection import  train_test_split
import tensorflow.keras as keras


# path to json file that stores the MFCC and genres labels for each processing segment
DATA_PATH = "music_data.json"

def load_data(data_path):
    with open(data_path, "r") as fp:
        data = json.load(fp)

    # convert list to numpy arrays
    X = np.array(data["mfcc"])
    y = np.array(data["labels"])

    print("Data succesfully loaded!")

    return X, y


if __name__ == '__main__':
    # load data
    X, y = load_data(DATA_PATH)

    # create train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    # build network topology
    model = keras.Sequential([
        # input layer
        keras.layers.Flatten(input_shape=(X.shape[1], X.shape[2])),

        # 1st dense layer, with 512 neurons
        keras.layers.Dense(512, activation='relu'),
        # 2st dense layer, with 256 neurons
        keras.layers.Dense(256, activation='relu'),
        # 3st dense layer
        keras.layers.Dense(64, activation='relu'),
        # output layer, 6 = 6 output, which is 6 genres
        keras.layers.Dense(6, activation='softmax') 

    ])

    #compile model
    optimiser = keras.optimizers.Adam(learning_rate=0.0001)
    model.compile(optimizer=optimiser, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # train model
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=32, epochs=50)
