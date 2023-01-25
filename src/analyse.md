## Document d'analyse pour la partie vectoridation des données synthétiques

### Principe et structure de donnée

en entrée, on a des données organisées sous la forme d'une table (par exemple provenant d'une BDD SQL).
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
4) le VAE et un espace latent borné jugé homogène de façon à pouvoir générer des données crédibles et statistiquement représentatives
5) un systéme de dévectorisation 

Au final, une fois l'entrainement fait, on livre juste :

* la partie encodeur du VAE
* des bornes pour l'espace latent et un moyen de le générer aléatoirement
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

ù Int : Identité ou catégorie 
* float : indentité tout le temps
* String : s'il y a un seul mot, alors on part sur une catégorie et on gère un dictionnaire
S'il y a beaucoup de mots différent, on pourra utiliser un encodeur/décodeur existant diminuer la taille du vecteur (?)
si la String est une phrase, alors il faudra réfléchir à un sytème plus complexe (RN récurrent avec VAE ??)
* Date : représentation spéciale avec : une vecteur de bit pour le jour de la semaine, le jour du mois, du mois, une indication de jour ferié, une indentité pour l'année.
* Autre Type ? : chaque type peut avoir tout comme les dates, une représentation judicieuse pour que l'on puisse regénérer des données statistiquement identiques.
le fait de faire ressortir les jours feriés pour les dates, est un bon exemple de donnée pertinante à rajouter sinon on passe peut être à coté de statistiques importantes qui se doivent d'être conservée.
Doit-on permettre de la flexibilité pour l'utilisateur final ?  


