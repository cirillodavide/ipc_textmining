from keras.layers import Lambda, Input, Dense
from keras import backend as K
from keras.models import Model
from keras.utils import plot_model,to_categorical
from keras.losses import mse, binary_crossentropy
import numpy as np
import gensim
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import argparse
import matplotlib.pyplot as plt

#load data
model = gensim.models.Word2Vec.load("data/medulloblastoma/word2vec.model")
filename = 'data/medulloblastoma/word2vec_words.txt'
with open(filename) as f:
    words = [line.strip() for line in f]
vec = []
for w in words:
    vec.append(model[w])
X = np.array(vec)
X = (X - X.min()) / (X.max() - X.min())

#words integer-encoding and then one-hot encoding
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(np.array(words))

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

#reparametrization trick
def sampling(args):
    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

# network parameters
input_size = len(X[0])
input_shape = (input_size, )
intermediate_dim = 10
batch_size = 128
latent_dim = 2
epochs = 50

#encoder
inputs = Input(shape=input_shape, name='encoder_input')
x = Dense(intermediate_dim, activation='relu')(inputs)
z_mean = Dense(latent_dim, name='z_mean')(x)
z_log_var = Dense(latent_dim, name='z_log_var')(x)

z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
encoder.summary()
plot_model(encoder, to_file='vae_mlp_encoder.png', show_shapes=True)

#decoder
latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
x = Dense(intermediate_dim, activation='relu')(latent_inputs)
outputs = Dense(input_size, activation='sigmoid')(x)

decoder = Model(latent_inputs, outputs, name='decoder')
decoder.summary()
plot_model(decoder, to_file='vae_mlp_decoder.png', show_shapes=True)

#VAE
outputs = decoder(encoder(inputs)[2])
vae = Model(inputs, outputs, name='vae_mlp')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    help_ = "Load h5 model trained weights"
    parser.add_argument("-w", "--weights", help=help_)
    help_ = "Use mse loss instead of binary cross entropy (default)"
    parser.add_argument("-m",
                        "--mse",
                        help=help_, action='store_true')
    args = parser.parse_args()
    models = (encoder, decoder)
    data = (x_test, y_test)

    # VAE loss = mse_loss or xent_loss + kl_loss
    if args.mse:
        reconstruction_loss = mse(inputs, outputs)
    else:
        reconstruction_loss = binary_crossentropy(inputs,
                                                  outputs)

    reconstruction_loss *= input_size
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)
    vae.compile(optimizer='adam')
    vae.summary()
    plot_model(vae,
               to_file='vae_mlp.png',
               show_shapes=True)

    if args.weights:
        vae.load_weights(args.weights)
    else:
        # train the autoencoder
        vae.fit(x_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(x_test, None))
        vae.save_weights('vae_mlp_mnist.h5')

    # display a 2D plot of the digit classes in the latent space
    z_test = encoder.predict(x_test, batch_size=batch_size)
    plt.figure(figsize=(6, 6))
    plt.scatter(z_test[:, 0], z_test[:, 1], c=y_test,
                alpha=.4, s=3**2, cmap='viridis')
    plt.colorbar()
    plt.show()
