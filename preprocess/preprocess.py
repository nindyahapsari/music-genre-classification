import json
import os
import librosa
import math

DATASET_PATH = "genre_dataset"
JSON_PATH = "data.json"  
SAMPLE_RATE = 22050
TRACK_DURATION = 30 # measure in second
SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION


# n_fft= 2048 and hop_length= 512 is the standart sample for analysing audio data
# num_segment -> to divide/slice the track into smaller part, creating more input data.

def save_mfcc(dataset_path, json_path, n_mfcc=13, n_fft=2048, hop_length=512, num_segments=5):

# build dictionary to store data

    data = {
        "mapping": [],
        "mfcc": [],
        "labels": []
    }

    num_sample_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    expected_num_mfcc_vector_per_segment = math.ceil(num_sample_per_segment / hop_length) # 1.2 -> 2

# loop through all the genres in the folders in files

    for i, (dirpath, dirnames, filenames) in enumerate(os.walk(dataset_path)):
        
        # ensure that we are not at the root level. We don't need the data in the root path
        if dirpath is not dataset_path:

            # save the semantic label
            dirpath_components = dirpath.split("\\")
            semantic_label = dirpath_components[-1]
            data["mapping"].append(semantic_label)
            print("\nProcessing: {}".format(semantic_label))

            # process files for a specific genre
            for f in filenames:
                # load audio files
                file_path = os.path.join(dirpath, f)
                signal, sample_rate = librosa.load(file_path, sr=SAMPLE_RATE)


                for s in range (num_segments):
                    start_sample = num_sample_per_segment * s #s=0 -> 0
                    finish_sample = start_sample + num_sample_per_segment # s=0 -> num_samples_per_segment

                    mfcc = librosa.feature.mfcc(signal[start_sample:finish_sample],
                                                sample_rate,
                                                n_fft=n_fft,
                                                n_mfcc=n_mfcc,
                                                hop_length=hop_length
                                                )
                    mfcc = mfcc.T

                    # store mfcc for segment if it has the expected length
                    if len(mfcc) == expected_num_mfcc_vector_per_segment:
                        data["mfcc"].append(mfcc.tolist())
                        data["labels"].append(i-1)
                        print("{}, segment:{}".format(file_path, s+1))
                    

    # save mfcc to json file
    with open(json_path, "w") as fp:
        json.dump(data, fp, indent=4)


if __name__=="__main__":
    save_mfcc(DATASET_PATH, JSON_PATH, num_segments=10)
