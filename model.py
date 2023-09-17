import tensorflow as tf
import pandas as pd

csv_file_path = 'game_states.csv'
data = pd.read_csv(csv_file_path)

data['key_up'].replace({'a': 0, 'd': 1}, inplace=True)
data['key_up'].fillna(2, inplace=True)
data['key_down'].replace({'LEFT': 0, 'RIGHT': 1}, inplace=True)
data['key_down'].fillna(2, inplace=True)

X = data.drop(columns=['point', 'key_up', 'key_down'])
y = data['key_up']  # Assuming we are training the model to imitate the 'up' paddle

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def create_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')  # Three output neurons for 3 actions
    ])
    
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model


input_shape = X_train.shape[1]
model = create_model(input_shape)


model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))


model.save('pong_game_model.h5')