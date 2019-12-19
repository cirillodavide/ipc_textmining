import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

from keras import backend as K

from keras.layers import Input, Dense, Lambda, Layer, Add, Multiply
from keras.models import Model, Sequential

import gensim
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


original_dim = 50
intermediate_dim = 10
latent_dim = 2
batch_size = 500
epochs = 50
epsilon_std = 1.0


def nll(y_true, y_pred):
    """ Negative log likelihood (Bernoulli). """

    # keras.losses.binary_crossentropy gives the mean
    # over the last axis. we require the sum
    #return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)
    return K.binary_crossentropy(y_true, y_pred)


class KLDivergenceLayer(Layer):

    """ Identity transform layer that adds KL divergence
    to the final model loss.
    """

    def __init__(self, *args, **kwargs):
        self.is_placeholder = True
        super(KLDivergenceLayer, self).__init__(*args, **kwargs)

    def call(self, inputs):

        mu, log_var = inputs

        kl_batch = - .5 * K.sum(1 + log_var -
                                K.square(mu) -
                                K.exp(log_var), axis=-1)

        self.add_loss(K.mean(kl_batch), inputs=inputs)

        return inputs


decoder = Sequential([
    Dense(intermediate_dim, input_dim=latent_dim, activation='relu'),
    Dense(original_dim, activation='sigmoid')
])

x = Input(shape=(original_dim,))
h1 = Dense(original_dim, activation='relu')(x)
h2 = Dense(original_dim, activation='relu')(h1)
h3 = Dense(intermediate_dim, activation='relu')(h2)
z_mu = Dense(latent_dim)(h3)
z_log_var = Dense(latent_dim)(h3)

#z_mu, z_log_var = KLDivergenceLayer()([z_mu, z_log_var])
z_sigma = Lambda(lambda t: K.exp(.5*t))(z_log_var)

eps = Input(tensor=K.random_normal(stddev=epsilon_std,
                                   shape=(K.shape(x)[0], latent_dim)))
z_eps = Multiply()([z_sigma, eps])
z = Add()([z_mu, z_eps])

x_pred = decoder(z)

vae = Model(inputs=[x, eps], outputs=x_pred)
vae.compile(optimizer='adam', loss=nll)

# train the VAE on MNIST digits
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

vae.fit(x_train,
        x_train,
        shuffle=True,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(x_test, x_test))

encoder = Model(x, z_mu)

# display a 2D plot of the digit classes in the latent space
z_test = encoder.predict(x_test, batch_size=batch_size)
plt.figure(figsize=(6, 6))
plt.scatter(z_test[:, 0], z_test[:, 1], c=y_test,
            alpha=.4, s=3**2, cmap='viridis')
plt.colorbar()
plt.show()
