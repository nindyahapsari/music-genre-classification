import json
import numpy as np
from sklearn.model_selection import  train_test_split
import tensorflow.keras as keras
import matplotlib.pyplot as plt

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

# ploting data into chart to see the overfitting problems
def plot_history(history):
    fig, axs = plt.subplots(2)

    # creating accuracy subplot
    axs[0].plot(history.history["accuracy"], label="train accuracy")
    axs[0].plot(history.history["val_accuracy"], label="test accuracy")
    axs[0].set_ylabel("Accuracy")
    axs[0].legend(loc="lower right")
    axs[0].set_title("Accuracy eval")

    #creating error subplot
    axs[1].plot(history.history["loss"], label="train error")
    axs[1].plot(history.history["val_loss"], label="test error")
    axs[1].set_ylabel("Error")
    axs[1].set_xlabel("Epoch")
    axs[1].legend(loc="upper right")
    axs[1].set_title("Error eval")

    plt.show()



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
        keras.layers.Dense(512, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)), keras.layers.Dropout(0.3),
        # 2st dense layer, with 256 neurons
        keras.layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)), keras.layers.Dropout(0.3),
        # 3st dense layer
        keras.layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)), keras.layers.Dropout(0.3),
        # output layer, 6 = 6 output, which is 6 genres
        keras.layers.Dense(6, activation='softmax') 

    ])

    #compile model
    optimiser = keras.optimizers.Adam(learning_rate=0.0001)
    model.compile(optimizer=optimiser, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # train model
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=32, epochs=100)

    # plot accuracy and error as a function of the epochs
    plot_history(history)
