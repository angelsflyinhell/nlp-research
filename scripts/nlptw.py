from datetime import datetime
import tensorflow as tf
import numpy as np

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical, pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam    
from tensorflow import keras

with open('./data/tweetdata.txt', encoding="utf8") as f:
    lines = f.read()

tokenizer = Tokenizer()
# data = "In which everything goes backwards \n in time and motion \n Palm trees shrink back into the ground \n Mangos become seeds \n and reappear in the eyes of Indian \n women \n The years go back \n cement becomes wood \n Panama hats are seen upon skeletons \n walking the plazas \n Of once again wooden benches \n The past starts..."
data = lines
corpus = data.lower().split("\n")

tokenizer.fit_on_texts(corpus)
total_words = len(tokenizer.word_index) + 1
# we add 1 to the length to include a placeholder for unknown words (OOV)

# create input sequences using list of tokens
input_sequences = []
for line in corpus:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# padding sequences
max_sequence_length = max([len(x) for x in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_length, padding='pre'))

# slice list by using the last element as the label
xs = input_sequences[:,:-1]
labels = input_sequences[:,-1]

ys = tf.keras.utils.to_categorical(labels, num_classes=total_words)

logdir = "logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)

model = Sequential()
model.add(Embedding(total_words,240, input_length=max_sequence_length-1))
model.add(Bidirectional(LSTM(150)))
model.add(Dense(total_words, activation='softmax'))
adam = Adam(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
history = model.fit(xs, ys, epochs=100, verbose=1, callbacks=[tensorboard_callback], use_multiprocessing=True)

model.save('./models/nlptw-1.h5')