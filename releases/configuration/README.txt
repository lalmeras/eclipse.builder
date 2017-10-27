
REALISE :

* editor : display line numbers
* editor : width = 120
* editor : show whitespace

* formatter : width = 120

* maven : disable download index repository at startup
* maven : enable update project at startup
* maven : editeur direct pour les pom.xml

* svn : decorators
* svn : quickdiff activé

* java perspective : sans Mylin, sans Declarations, avec Console, avec Tasks

* package explorer : link with editor
* package explorer : hierarchical

* afficher le garbage collector (asauvez, afievee, nbarithel)

* search : enlever les onglets superflus

* enable spell checking : false

* xml editor : longueur de ligne plus conséquente (par défaut 72, => 200)

* console : augmenter le nombre de lignes à 80.000 ou 800.000

A TESTER :

* java : perspective, ajouter la vue Servers
* search : intégrer une liste de patterns pour les fichiers textes usuels

A FAIRE :

* fonte

PROPOSITIONS :

REJETE :

* integration jade (decompilateur) ? (asauvez)
* revoir les warn / errors : exemples :
  * missing @Override en warn
  * unnecessary cast / import en error
  * ignore missing serializable version uid
  * enum non utilisé dans un switch : error
* ajouter la vue outline sur le debug

NOTES :

* tomcat : augmenter les timeouts par défaut et désactiver l'auto-deploy
Impossible ou très difficile. Les timeout sont définis sur les
extension-point. Le auto-deploy est en dur (new WebModule(..., true))
