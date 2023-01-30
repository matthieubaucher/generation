## Document d'analyse pour la partie vectoridation des données synthétiques

### Principe et structure de donnée

en entrée, on a des données organisées sous la forme d'une table (par exemple provenant d'une BDD SQL).
Le cas avec plusieures tables et jointures sera traité postérieurement.
toutes les données sont dans un fichier : le nom de la table, les noms de colonne, leur type (éventuellement), et toutes les lignes de la table.
le fichier peut avoir plusieurs sources : json ou autre ... 
en sortie, on veut un ensemble de grands vecteurs utilisables par une réseau de neurone.
Chaque grand vecteur représente une ligne de la table.
Chaque grand vecteur est une concaténation de plusieurs sous-vecteur.
Chaque sous-vecteur représente une donnée de la ligne (une cellule)
Le réseau de neurone cible, est un VAE. il apprendra a créer une représentation pour chaque entrée.
l'espace latent permettra plus tard de générer de nouvelles données et c'est juste la partie encodeur qui sera stockée et non pas les vecteurs d'entrées qui ont servi a l'apprentissage.
le VAE produit un grand vecteur lui aussi et on doit pouvoir faire l'opération inverse consistant a retrouver les données d'origine.
bien ce sont des données générées et elles ne sont pas sensé être identiques aux données d'origine mais juste semblable.

### livrable 

ce qui est attendu c'est donc :
1) un système de lecture de fichier en entrée quelque soit le type (json ou autre) permettant de créer une structure métier représentant la table a vectoriser.
2) un process de vectorisation
3) l'utilisation de 1 et 2 pour obtenir les données d'entrainement   
4) le VAE qui génére des données crédibles et statistiquement représentatives en se basant sur un espace latent généré aléatoirement
5) l'espace latent n'a pas de densité de probabilité homogène. je suggère l'utilisation d'un GAN pour déterminer si une config a une chance
   d'exister : si ca renvoie 0.8 alors on rejette l'entrée générée avec une proba de 0.2 et on regénère une nouvelle entrée si c'est le cas.
   cette méthode par rejet permet de garrantir que les probabilités seront conservée.
6) un systéme de dévectorisation 

Au final, une fois l'entrainement fait, on livre juste :

* un générateur d'espace latent aléatoire utilisant une méthode de rejet qui a été entrainé via un GAN
* la partie encodeur du VAE
* le système de dévectorisation

### principe de vectorisation des données

chaque cellule a une colonne qui a éventuellement un type (il peut ne pas être fourni) et un sous-type.

les types possibles sont des types natifs classiques :
Int, Float, String et Date

les sous types donnent plus d'info :
Identité ou Catégorie
un catégorie correspond a un nombre limité de possibilité et doit être interprété de façon discrete par le RN
ex : Int si il n'y a que 5 possibilités doit être représenté par un vecteur de dimension (5,) tout à 0 sauf le celui à l'indice concerné qui vaut 1.
Par contre si Int contient des grands nombre ou s'il y en a beaucoup, alors on transforme en vecteur de taille (1,) contenant juste le nombre (= identité).

on détermine le type et le sous-type en analysant les données fournies ; mais l'utilisateur doit pouvoir spécifier dans le fichier les sous-types qu'il veut forcer.

### Stratégie de vectorisation pour chaque type :

* Int : Identité ou catégorie 
* float : indentité tout le temps
* String : s'il y a un seul mot, alors on part sur une catégorie et on gère un dictionnaire
S'il y a beaucoup de mots différent, on pourra utiliser un encodeur/décodeur existant diminuer la taille du vecteur (?)
si la String est une phrase, alors il faudra réfléchir à un sytème plus complexe (RN récurrent avec VAE ??)
* Date : représentation spéciale avec : une vecteur de bit pour le jour de la semaine, le jour du mois, du mois, une indication de jour férié, une indentité pour l'année.
* Autre Type ? : chaque type peut avoir tout comme les dates, une représentation judicieuse pour que l'on puisse regénérer des données statistiquement identiques.
le fait de faire ressortir les jours feriés pour les dates, est un bon exemple de donnée pertinante à rajouter sinon on passe peut être à coté de relations entre les éléments de la table qui doivent être 
  conservée avec la même probabilité.
On doit ainsi permettre à l'utilisateur de spécifier certains éléments importants de chaque donnée sous-jacentes : 
  Comme on fait pour les dates, il pourrait vouloir créer des propriétés à rajouter en plus de la donnée de base (ex: "le jour est-il férié ?" ,"le jour de la semaine", etc ...)
=> on doit créer une GUI pour associer à chaque champs une liste d'expression interprété. celles ci sont ajoutées à la donnée de base (voir la remplace ?).
  

### Implantation technique

Sur une base Java, création d'un service REST via SpringBoot 5, celui-ci doit fournir diverses fonctions :
* création d'un générateur ENTREE = (nom du générateur) SORTIE = ID du générateur
* ajout d'une table (ID du générateur, un fichier contenant sa définition)  
* ajout d'une propriété (ID du générateur, nom de la table, nom de colonne, code de la fonction avec une syntaxe compatible Jeval)
* récupération des méta-data (ID du générateur) SORTIE = les tables et leur colonnes avec leur type, sous-type et leurs propriétés ajoutées ID inclus
* ajout d'une PK (ID du générateur, nom de la table, liste des noms de colonnes)  
* suppression d'une propriété (ID du générateur, ID de la propriété)
* suppression d'une table (ID du générateur, nom de la table)
* suppression d'un générateur (ID du générateur)
* suppression des data d'un générateur (ID du générateur)  pour supprimer uniquement les lignes mais pas les méta-data
* génération du générateur (ID du générateur) SORTIE : un jar contenant le générateur

Sur une technologie quelconque (java/swing ou client web ou page web fourni par le tomcat embarqué par spring) :
* création d'une GUI utilisant notre service 
  
Sur du python/pytorch :
* implantation d'un VAE qui s'adapte aux dimension d'entrée d'une seule table, le processus s'entraine et fournit :
  1) le tenseur de l'espace latent
  2) sa partie encodeur  
* implantation du GAN qui prend en paramétre le tenseur de l'espace latent, détermine les bornes min et max de chaque cellule, et produit un 
  générateur d'espace latent aléatoire, puis s'entraine a reconnaitre les données produites par lui plutot que par les données réelles du tenseur.
  ainsi il créer une fonction qui, pour un donnée générée determine sa probabilité d'exister. 
  1) un générateur d'espace latent aléatoire avec filtrage pour qu'il soit statistiquement représentatif

Sur du java :
* encapsulation du python qui permet d'avoir des méthodes java qui délègue l'IA au python
suivant les technologies utilisées :

DL4J/TensorFlow/Keras :
- utilisation de DL4J pour créer un tenseur à partir des données de la table
- écriture sur disque du tenseur sur lequel le VAE va s'entrainer
- éventuellement : utilisation de DL4J pour charger le modèle Keras en .h5 et l'exécuter sur le tenseur pour l'entrainement   
- sinon : utilisation de DL4J pour lancer le script keras ; celui-ci lit le tenseur sur le disque
- dans tous les cas, à la fin le script enregistre l'encodeur et le gan sur disque
- DL4J charge les deux modèles et crée un objet générateur, le serialise et l'envoie
liens utiles :
  https://deeplearning4j.konduit.ai/
  https://towardsdatascience.com/deploying-keras-deep-learning-models-with-java-62d80464f34a

DJL/tensorFlow/Keras :
- chargement des modèles VAE et GAN via DJL
les scipts Keras doivent sauvegarder ainsi :
  loaded_model = keras.models.load_model("resnet.h5")
  tf.saved_model.save(loaded_model, "resnet/1/")
pour le chargement voir la doc ici :
  https://docs.djl.ai/docs/load_model.html

DJL/Pytorch :
- chargement des modèles VAE et GAN via DJL  
les scipts Keras doivent sauvegarder ainsi (c'est du torchScript) :
  traced_script_module.save("traced_resnet_model.pt")
pour le chargement c'est pareil que pour keras d'apres la doc :
  http://docs.djl.ai/docs/pytorch/how_to_convert_your_model_to_torchscript.html
  https://docs.djl.ai/docs/load_model.html

* génération d'un jar exécutable par le client lorsque l'on génére un générateur
* stockage des informations du générateur en mémoire dans une map sérialisable (c'est suffisant à voir si on ajoute une base NoSQL) et des jars des générateurs sur disque. 

### Etapes du projet 

* JAVA : réalisation d'un lecteur d'un json représentant une table, création d'un objet pivot qui la représente
* création d'un pivot correct pour nos essais
* réalisation d'un certain nombre de POC pour montrer que l'on peut faire chaque partie du projet
- essai de fonctionnement d'un script Keras sur notre env de dev : voir les installations requises 
- essai de fonctionnement d'un script Pytorch sur notre env de dev : voir les installations requises
- normaliser nos installations sur windows : quelle méthode ?  
- essai Keras ou Pytorch pour le VAE (qu'est ce qui est le plus simple ? on essaie les deux ?)
- essai GAN (Keras ou Pytorch) pour avoir des proba crédibles : est-ce une bonne solution ?
- création d'un tenseur en DL4J à partir d'un pivot, sauvegarde, chargement
- montrer que l'on peut sauvegarder et lire un script Keras avec DL4J et utilisation d'un tenseur
- création d'un tenseur en DJL à partir d'un pivot, sauvegarde, chargement
- montrer que l'on peut sauvegarder et lire un script Keras avec DJL
- montrer que l'on peut sauvegarder et lire un script Pytorch avec DJL
- montrer que l'on peut créer un jar exécutable coté client permettant d'embarquer nos scipt python : quelle version de java ? 11 ? 
* voir quelle techno on utilise finalement 
* JAVA + SpringBoot : création du service. interfaces + code en dummy pour commencer.
* implantation de la solution définitive en python
* implantation de la solution en java 


### évolution futures

* gestion des textes : doit-on générer un VAE ou un LSTM pour chaque colonne de façon à reproduire des textes crédibles ?
* anonymisation de certains champs : on peut ajouter au service une méthode pour spécifier une colonne à anonymiser
* gestion de plusieures tables et de leurs jointures, la aussi il faut respecter les probabilités et éviter des champs sans correspondances.
  (on est plus sur un dev java la ...)
par exemple une table ACHAT de peut mentionner un client qui n'existe pas dans la table CLIENT. 
* gestion d'autres contraintes de base de donnée   

