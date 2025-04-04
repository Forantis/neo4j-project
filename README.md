# Application Neo4j avec Flask - TP NoSQL

Cette application implémente une API RESTful avec Flask et Neo4j pour gérer un réseau social simple avec des utilisateurs, des posts et des commentaires.

## Prérequis

- Python 3.8+
- Docker
- Neo4j (via Docker ou installation locale)
- Postman pour tester l'API

## Installation

1. **Cloner le dépôt ou télécharger les fichiers dans un répertoire**
   ```bash
   git clone git@github.com:Forantis/neo4j-project.git
   cd tp02
   ```

2. **Installer les dépendances nécessaires**
   ```bash
   pip install -r requirements.txt
   ```

(Attention: en cas de besoin il faut passer dans l'environnement Python avant le pip : )
```bash
   source ./bin/activate
```

3. **Démarrer Neo4j avec Docker**
   ```bash
   docker run --name neo4j -d \
   -p 7474:7474 -p 7687:7687 \
   -e NEO4J_AUTH=neo4j/password \
   neo4j
   ```

4. **Lancer l'application Flask**
   ```bash
   flask --app app run
   ```

   L'API sera accessible à l'adresse suivante : [http://localhost:5000](http://localhost:5000)

## Structure du projet

- `app.py` : Fichier principal contenant les routes de l'API Flask.
- `models.py` : Définit les modèles pour les utilisateurs, les posts et les commentaires.
- `requirements.txt` : Liste des dépendances Python nécessaires.
- `README.md` : Documentation du projet.

## Tester l'API avec Postman

### Étapes générales

1. **Ouvrir Postman**
2. **Créer une nouvelle collection**
3. **Ajouter une requête pour chaque endpoint de l'API**
4. **Configurer les requêtes avec les méthodes HTTP appropriées (GET, POST, PUT, DELETE)**
5. **Ajouter les en-têtes et le corps de la requête si nécessaire**
6. **Envoyer les requêtes et vérifier les réponses**

### Routes pour les utilisateurs

#### 1. Créer un utilisateur
- **Méthode** : POST
- **URL** : `http://localhost:5000/users`
- **Body (JSON)** :
  ```json
  {
      "name": "Alice Dupont",
      "email": "alice@example.com"
  }
  ```

#### 2. Récupérer tous les utilisateurs
- **Méthode** : GET
- **URL** : `http://localhost:5000/users`

#### 3. Récupérer un utilisateur par son ID
- **Méthode** : GET
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}`

#### 4. Mettre à jour un utilisateur
- **Méthode** : PUT
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}`
- **Body (JSON)** :
  ```json
  {
      "name": "Alice Modifié",
      "email": "alice.modifie@example.com"
  }
  ```

#### 5. Supprimer un utilisateur
- **Méthode** : DELETE
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}`

#### 6. Ajouter un ami
- **Méthode** : POST
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/friends`
- **Body (JSON)** :
  ```json
  {
      "friend_id": "{ID_AMI}"
  }
  ```

#### 7. Récupérer les amis d'un utilisateur
- **Méthode** : GET
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/friends`

#### 8. Vérifier si deux utilisateurs sont amis
- **Méthode** : GET
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/friends/{ID_AMI}`

#### 9. Récupérer les amis en commun
- **Méthode** : GET
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/mutual-friends/{ID_AUTRE_UTILISATEUR}`

#### 10. Supprimer un ami 
- **Méthode** : DELETE  
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/friends/{ID_AMI}`  
- **Description** : Supprime un ami d'un utilisateur.  
- **Exemple de réponse (JSON)** :  
    ```json
    {
            "message": "Ami supprimé avec succès"
    }
    ```

### Routes pour les posts

#### 1. Créer un post
- **Méthode** : POST
- **URL** : `http://localhost:5000/users/{ID_UTILISATEUR}/posts`
- **Body (JSON)** :
  ```json
  {
      "title": "Mon premier post",
      "content": "Contenu de mon premier post"
  }
  ```

#### 2. Récupérer tous les posts
- **Méthode** : GET
- **URL** : `http://localhost:5000/posts`

#### 3. Récupérer un post par son ID
- **Méthode** : GET
- **URL** : `http://localhost:5000/posts/{ID_POST}`

#### 4. Mettre à jour un post
- **Méthode** : PUT
- **URL** : `http://localhost:5000/posts/{ID_POST}`
- **Body (JSON)** :
  ```json
  {
      "title": "Post modifié",
      "content": "Contenu modifié"
  }
  ```

#### 5. Supprimer un post
- **Méthode** : DELETE
- **URL** : `http://localhost:5000/posts/{ID_POST}`

#### 6. Ajouter un like à un post
- **Méthode** : POST
- **URL** : `http://localhost:5000/posts/{ID_POST}/like`
- **Body (JSON)** :
  ```json
  {
      "user_id": "{ID_UTILISATEUR}"
  }
  ```

#### 7. Retirer un like d'un post
- **Méthode** : DELETE
- **URL** : `http://localhost:5000/posts/{ID_POST}/like`
- **Body (JSON)** :
  ```json
  {
      "user_id": "{ID_UTILISATEUR}"
  }
  ```

### Routes pour les commentaires

#### 1. Ajouter un commentaire à un post
- **Méthode** : POST
- **URL** : `http://localhost:5000/posts/{ID_POST}/comments`
- **Body (JSON)** :
  ```json
  {
      "content": "Super post !",
      "user_id": "{ID_UTILISATEUR}"
  }
  ```

#### 2. Récupérer les commentaires d'un post
- **Méthode** : GET
- **URL** : `http://localhost:5000/posts/{ID_POST}/comments`

#### 3. Mettre à jour un commentaire
- **Méthode** : PUT
- **URL** : `http://localhost:5000/comments/{ID_COMMENT}`
- **Body (JSON)** :
  ```json
  {
      "content": "Commentaire modifié"
  }
  ```

#### 4. Supprimer un commentaire
- **Méthode** : DELETE
- **URL** : `http://localhost:5000/comments/{ID_COMMENT}`

#### 5. Ajouter un like à un commentaire
- **Méthode** : POST
- **URL** : `http://localhost:5000/comments/{ID_COMMENT}/like`
- **Body (JSON)** :
  ```json
  {
      "user_id": "{ID_UTILISATEUR}"
  }
  ```

#### 6. Retirer un like d'un commentaire
- **Méthode** : DELETE
- **URL** : `http://localhost:5000/comments/{ID_COMMENT}/like`
- **Body (JSON)** :
  ```json
  {
      "user_id": "{ID_UTILISATEUR}"
  }
  ```

## Dépannage

### Problème de connexion à Neo4j
- Vérifiez que le conteneur Docker est en cours d'exécution avec `docker ps`.
- Assurez-vous que les ports 7474 et 7687 sont bien exposés.
- Vérifiez les logs du conteneur avec `docker logs neo4j`.

### Erreurs d'authentification
- Vérifiez que les identifiants utilisés dans `models.py` correspondent à ceux définis lors du lancement du conteneur.

### Erreurs lors des requêtes API
- Vérifiez la syntaxe JSON des corps de requêtes.
- Assurez-vous que les IDs utilisés dans les URLs existent bien dans la base de données.
