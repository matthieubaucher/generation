import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt
from VAENombre import Sampling, VAE


PATH_APPLICATION = "../../"
PATH_RESOURCES = PATH_APPLICATION + "/resources/"
filename = PATH_RESOURCES + 'POC_UTILISATION_D_UN_VAE_KERAS'


def plot_label_clusters(vae, data, labels):
    # display a 2D plot of the digit classes in the latent space
    z_mean, _, _ = vae.encoder.predict(data)
    plt.figure(figsize=(12, 10))
    plt.scatter(z_mean[:, 0], z_mean[:, 1], c=labels)
    plt.colorbar()
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.show()


(x_train, y_train), _ = keras.datasets.mnist.load_data()
x_train = np.expand_dims(x_train, -1).astype("float32") / 255

vae = keras.models.load_model(filename, custom_objects={'Sampling': Sampling,
                                                        'VAE': VAE})

plot_label_clusters(vae, x_train, y_train)
