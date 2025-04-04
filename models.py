from py2neo import Graph, Node, Relationship
from datetime import datetime
import uuid

# Connect to Neo4j database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

def dict_to_node(label, properties):
    """
    Convert a dictionary to a Neo4j Node.
    :param label: The label of the node (e.g., "User", "Post").
    :param properties: A dictionary of properties for the node.
    :return: A py2neo Node object.
    """
    if not isinstance(properties, dict):
        raise ValueError("Properties must be a dictionary")
    return Node(label, **properties)

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = datetime.now().timestamp()
        self.id = str(uuid.uuid4())

    def save(self):
        # Vérifiez si l'utilisateur existe déjà
        existing_user = User.find_by_id(self.id)
        if (existing_user):
            return self  # Ne recrée pas l'utilisateur s'il existe déjà
        
        # Crée un nouvel utilisateur si inexistant
        user_node = Node("User",
                        id=self.id,
                        name=self.name,
                        email=self.email,
                        created_at=self.created_at)
        graph.create(user_node)
        return self
    
    @staticmethod
    def find_all():
        query = "MATCH (u:User) RETURN properties(u) AS user"
        return [record["user"] for record in graph.run(query)]
    
    @staticmethod
    def find_by_id(user_id):
        query = "MATCH (u:User {id: $id}) RETURN properties(u) AS user"
        result = graph.run(query, id=user_id).data()
        return result[0]["user"] if result else None
    
    @staticmethod
    def update(user_id, name=None, email=None):
        update_query = "MATCH (u:User {id: $id})"
        if name and email:
            update_query += " SET u.name = $name, u.email = $email"
            graph.run(update_query, id=user_id, name=name, email=email)
        elif name:
            update_query += " SET u.name = $name"
            graph.run(update_query, id=user_id, name=name)
        elif email:
            update_query += " SET u.email = $email"
            graph.run(update_query, id=user_id, email=email)
        
        return User.find_by_id(user_id)
    
    @staticmethod
    def delete(user_id):
        # First delete all relationships
        graph.run("MATCH (u:User {id: $id})-[r]-() DELETE r", id=user_id)
        # Then delete the user node
        graph.run("MATCH (u:User {id: $id}) DELETE u", id=user_id)
    
    @staticmethod
    def add_friend(user_id, friend_id):
        query = """
        MATCH (u:User {id: $user_id}), (f:User {id: $friend_id})
        MERGE (u)-[r:FRIENDS_WITH]->(f)
        RETURN u, f
        """
        return graph.run(query, user_id=user_id, friend_id=friend_id).data()
    
    @staticmethod
    def remove_friend(user_id, friend_id):
        query = """
        MATCH (u:User {id: $user_id})-[r:FRIENDS_WITH]-(f:User {id: $friend_id})
        DELETE r
        """
        graph.run(query, user_id=user_id, friend_id=friend_id)
    
    @staticmethod
    def get_friends(user_id):
        query = """
        MATCH (u:User {id: $user_id})-[:FRIENDS_WITH]-(f:User)
        RETURN properties(f) AS friend
        """
        return [record["friend"] for record in graph.run(query, user_id=user_id)]
    
    @staticmethod
    def are_friends(user_id, friend_id):
        query = """
        MATCH (u:User {id: $user_id})-[r:FRIENDS_WITH]-(f:User {id: $friend_id})
        RETURN COUNT(r) > 0 as are_friends
        """
        result = graph.run(query, user_id=user_id, friend_id=friend_id).data()
        return result[0]["are_friends"] if result else False
    
    @staticmethod
    def get_mutual_friends(user_id, other_id):
        query = """
        MATCH (u:User {id: $user_id})-[:FRIENDS_WITH]-(mutual:User)-[:FRIENDS_WITH]-(other:User {id: $other_id})
        RETURN properties(mutual) AS mutual_friend
        """
        return [record["mutual_friend"] for record in graph.run(query, user_id=user_id, other_id=other_id)]


class Post:
    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.created_at = datetime.now().timestamp()
        self.user_id = user_id
        self.id = str(uuid.uuid4())
    
    def save(self):
        # Crée le nœud du post
        post_node = Node("Post",
                        id=self.id,
                        title=self.title,
                        content=self.content,
                        created_at=self.created_at)
        
        # Trouve l'utilisateur
        user_dict = User.find_by_id(self.user_id)
        if not user_dict:
            raise ValueError(f"User with id {self.user_id} not found")
        
        # Convertit le dictionnaire utilisateur en nœud
        user_node = graph.evaluate("MATCH (u:User {id: $id}) RETURN u", id=self.user_id)
        
        # Crée la relation
        created_rel = Relationship(user_node, "CREATED", post_node)
        
        # Ajoute le post et la relation dans la base de données
        tx = graph.begin()
        tx.create(post_node)
        tx.create(created_rel)
        tx.commit()
        
        return self
        
    @staticmethod
    def find_all():
        query = "MATCH (p:Post) RETURN properties(p) AS post"
        return [record["post"] for record in graph.run(query)]
    
    @staticmethod
    def find_by_id(post_id):
        query = "MATCH (p:Post {id: $id}) RETURN properties(p) AS post"
        result = graph.run(query, id=post_id).data()
        return result[0]["post"] if result else None
    
    @staticmethod
    def find_by_user(user_id):
        query = """
        MATCH (u:User {id: $user_id})-[:CREATED]->(p:Post)
        RETURN properties(p) AS post
        """
        return [record["post"] for record in graph.run(query, user_id=user_id)]
    
    @staticmethod
    def update(post_id, title=None, content=None):
        update_query = "MATCH (p:Post {id: $id})"
        if title and content:
            update_query += " SET p.title = $title, p.content = $content"
            graph.run(update_query, id=post_id, title=title, content=content)
        elif title:
            update_query += " SET p.title = $title"
            graph.run(update_query, id=post_id, title=title)
        elif content:
            update_query += " SET p.content = $content"
            graph.run(update_query, id=post_id, content=content)
        
        return Post.find_by_id(post_id)
    
    @staticmethod
    def delete(post_id):
        # First delete all relationships
        graph.run("MATCH (p:Post {id: $id})-[r]-() DELETE r", id=post_id)
        # Then delete the post node
        graph.run("MATCH (p:Post {id: $id}) DELETE p", id=post_id)
    
    @staticmethod
    def add_like(post_id, user_id):
        query = """
        MATCH (u:User {id: $user_id}), (p:Post {id: $post_id})
        MERGE (u)-[r:LIKES]->(p)
        RETURN u, p
        """
        return graph.run(query, user_id=user_id, post_id=post_id).data()
    
    @staticmethod
    def remove_like(post_id, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[r:LIKES]->(p:Post {id: $post_id})
        DELETE r
        """
        graph.run(query, user_id=user_id, post_id=post_id)


class Comment:
    def __init__(self, content, user_id, post_id):
        self.content = content
        self.created_at = datetime.now().timestamp()
        self.user_id = user_id
        self.post_id = post_id
        self.id = str(uuid.uuid4())
    
    def save(self):
        # Create comment node
        comment_node = Node("Comment",
                          id=self.id,
                          content=self.content,
                          created_at=self.created_at)
        
        # Find the user and post
        user = User.find_by_id(self.user_id)
        post = Post.find_by_id(self.post_id)
        
        if not user:
            raise ValueError(f"User with id {self.user_id} not found")
        if not post:
            raise ValueError(f"Post with id {self.post_id} not found")
        
        # Create relationships
        created_rel = Relationship(user, "CREATED", comment_node)
        has_comment_rel = Relationship(post, "HAS_COMMENT", comment_node)
        
        # Create everything in the database
        tx = graph.begin()
        tx.create(comment_node)
        tx.create(created_rel)
        tx.create(has_comment_rel)
        tx.commit()
        
        return self
    
    @staticmethod
    def find_all():
        query = "MATCH (c:Comment) RETURN properties(c) AS comment"
        return [record["comment"] for record in graph.run(query)]
    
    @staticmethod
    def find_by_id(comment_id):
        query = "MATCH (c:Comment {id: $id}) RETURN properties(c) AS comment"
        result = graph.run(query, id=comment_id).data()
        return result[0]["comment"] if result else None
    
    @staticmethod
    def find_by_post(post_id):
        query = """
        MATCH (p:Post {id: $post_id})-[:HAS_COMMENT]->(c:Comment)
        RETURN properties(c) AS comment
        """
        return [record["comment"] for record in graph.run(query, post_id=post_id)]
    
    @staticmethod
    def update(comment_id, content=None):
        if content:
            update_query = "MATCH (c:Comment {id: $id}) SET c.content = $content"
            graph.run(update_query, id=comment_id, content=content)
        
        return Comment.find_by_id(comment_id)
    
    @staticmethod
    def delete(comment_id):
        # First delete all relationships
        graph.run("MATCH (c:Comment {id: $id})-[r]-() DELETE r", id=comment_id)
        # Then delete the comment node
        graph.run("MATCH (c:Comment {id: $id}) DELETE c", id=comment_id)
    
    @staticmethod
    def add_like(comment_id, user_id):
        query = """
        MATCH (u:User {id: $user_id}), (c:Comment {id: $comment_id})
        MERGE (u)-[r:LIKES]->(c)
        RETURN u, c
        """
        return graph.run(query, user_id=user_id, comment_id=comment_id).data()
    
    @staticmethod
    def remove_like(comment_id, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[r:LIKES]->(c:Comment {id: $comment_id})
        DELETE r
        """
        graph.run(query, user_id=user_id, comment_id=comment_id)
