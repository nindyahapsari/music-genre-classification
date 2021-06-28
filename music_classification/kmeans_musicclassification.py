import glob
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import librosa
from sklearn.cluster import KMeans

# helper methods #

def loadMusics(filePath):
    musics = []
    for path in filePath:
        X, sr = librosa.load(path)
        musics.append(X)
    return musics

def featureExtraction(fileName):
    raw, rate = librosa.load(fileName)
    stft = np.abs(librosa.stft(raw))
    mfcc = np.mean(librosa.feature.mfcc(y=raw,sr=rate,n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=rate).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(raw, sr=rate).T, axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=rate).T, axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(raw), sr=rate).T, axis=0)
    return mfcc, chroma, mel, contrast, tonnetz

# takes parent directory name, subdirectory within  parent directory, and file extension as input.

def parseAudio(parentDirectory, subDirectories, fileExtension="*.wav"):
    features, labels = np.empty((0,193)), np.empty(0)
    for subDir in subDirectories:
        for fn in glob.glob(os.path.join(parentDirectory, subDir, fileExtension)):
            mfcc, chroma, mel, contrast, tonnetz = featureExtraction(fn)
            tempFeatures = np.hstack([mfcc, chroma, mel, contrast, tonnetz])
            features = np.vstack([features, tempFeatures])
            # pop = 1, classical = 2, hiphop=3, rock=0
            if subDir == "pop":
                labels = np.append(labels,1)
            elif subDir == "classical":
                labels = np.append(labels, 2)
            elif subDir == "hiphop":
                labels = np.append(labels, 3)
            else :
                labels = np.append(labels, 0)
        return np.array(features), np.array(labels, dtype=np.int)

training = "training_dataset"
test = "test_dataset"
subDirectories = ["pop", "classical", "hiphop", "rock"]
trainingFeatures, trainingLabels = parseAudio(training, subDirectories)
testFeatures, testLabels = parseAudio(test, subDirectories)


# training loop #
model = KMeans(n_clusters=4)
model.fit(trainingFeatures)

# test results #
print(model.labels_)

