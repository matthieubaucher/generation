import numpy as np
from tensorflow import keras
from POC_UTILISATION_D_UN_VAE_KERAS.VAENombre import VAE, encoder, decoder

print("definition de l'espace de stockage")

PATH_APPLICATION = "../../"
PATH_RESOURCES = PATH_APPLICATION + "/resources/"
filename = PATH_RESOURCES + 'POC_UTILISATION_D_UN_VAE_KERAS'

print("filename = " + filename)

print("chargement du dataset")
(x_train, _), (x_test, _) = keras.datasets.mnist.load_data()
mnist_digits = np.concatenate([x_train, x_test], axis=0)
mnist_digits = np.expand_dims(mnist_digits, -1).astype("float32") / 255

print("creation du VAE")
vae = VAE(encoder, decoder)
print("compilation du VAE")
vae.compile(optimizer=keras.optimizers.Adam())
print("entrainement du VAE")
vae.fit(mnist_digits, epochs=30, batch_size=128)
print("sauvegarde du VAE")
vae.save(filename, mnist_digits)
