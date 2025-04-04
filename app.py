from flask import Flask, request, jsonify
from models import User, Post, Comment
import json

app = Flask(__name__)

# Helper function to convert Neo4j nodes to dictionaries
def node_to_dict(node):
    import json
    
    # Si c'est None, retourner un dictionnaire vide
    if node is None:
        return {}
    
    # Pour les dictionnaires, la façon la plus sûre est de les filtrer pour ne garder que les données sérialisables
    if isinstance(node, dict):
        try:
            # Tester si le dictionnaire est JSON sérialisable
            json.dumps(node)
            return node
        except TypeError:
            # Si non sérialisable, filtrer les valeurs non sérialisables
            return {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                   for k, v in node.items()}
    
    # Pour les objets avec __dict__ (comme vos classes modèles)  
    if hasattr(node, '__dict__'):
        obj_dict = {k: v for k, v in node.__dict__.items() if not k.startswith('_')}
        # Filtrer les valeurs non sérialisables
        return {k: str(v) if not isinstance(v, (str, int, float, bool, type(None), dict, list)) else v 
                for k, v in obj_dict.items()}
    
    # Pour les objets py2neo Node
    try:
        return dict(node)
    except Exception:
        # Dernier recours - essayer de sérialiser comme une chaîne
        return {"data": str(node)}
    
# Routes for Users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.find_all()
    return jsonify([node_to_dict(user) for user in users])

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({"error": "Name and email required"}), 400
    
    try:
        user = User(name=data['name'], email=data['email']).save()
        return jsonify(node_to_dict(user)), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(node_to_dict(user))

@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        updated_user = User.update(user_id, 
                                  name=data.get('name'), 
                                  email=data.get('email'))
        return jsonify(node_to_dict(updated_user))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        User.delete(user_id)
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Friend routes
@app.route("/users/<user_id>/friends", methods=["GET"])
def get_friends(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        friends = User.get_friends(user_id)
        return jsonify([node_to_dict(friend) for friend in friends])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/friends", methods=["POST"])
def add_friend(user_id):
    data = request.json
    if not data or not data.get('friend_id'):
        return jsonify({"error": "Friend ID required"}), 400
    
    friend_id = data['friend_id']
    
    if user_id == friend_id:
        return jsonify({"error": "Cannot add yourself as a friend"}), 400
    
    user = User.find_by_id(user_id)
    friend = User.find_by_id(friend_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not friend:
        return jsonify({"error": "Friend not found"}), 404
    
    try:
        result = User.add_friend(user_id, friend_id)
        return jsonify({"message": "Friend added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/friends/<friend_id>", methods=["DELETE"])
def remove_friend(user_id, friend_id):
    user = User.find_by_id(user_id)
    friend = User.find_by_id(friend_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not friend:
        return jsonify({"error": "Friend not found"}), 404
    
    try:
        User.remove_friend(user_id, friend_id)
        return jsonify({"message": "Friend removed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/friends/<friend_id>", methods=["GET"])
def check_friendship(user_id, friend_id):
    user = User.find_by_id(user_id)
    friend = User.find_by_id(friend_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not friend:
        return jsonify({"error": "Friend not found"}), 404
    
    try:
        are_friends = User.are_friends(user_id, friend_id)
        return jsonify({"are_friends": are_friends})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/mutual-friends/<other_id>", methods=["GET"])
def get_mutual_friends(user_id, other_id):
    user = User.find_by_id(user_id)
    other = User.find_by_id(other_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not other:
        return jsonify({"error": "Other user not found"}), 404
    
    try:
        mutual_friends = User.get_mutual_friends(user_id, other_id)
        return jsonify([node_to_dict(friend) for friend in mutual_friends])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Post routes
@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.find_all()
    return jsonify([node_to_dict(post) for post in posts])

@app.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.find_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(node_to_dict(post))

@app.route("/users/<user_id>/posts", methods=["GET"])
def get_user_posts(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        posts = Post.find_by_user(user_id)
        return jsonify([node_to_dict(post) for post in posts])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/posts", methods=["POST"])
def create_post(user_id):
    data = request.json
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content required"}), 400
    
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        post = Post(title=data['title'], 
                   content=data['content'], 
                   user_id=user_id).save()
        return jsonify(node_to_dict(post)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    post = Post.find_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    try:
        updated_post = Post.update(post_id, 
                                  title=data.get('title'), 
                                  content=data.get('content'))
        return jsonify(node_to_dict(updated_post))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.find_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    try:
        Post.delete(post_id)
        return jsonify({"message": "Post deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    data = request.json
    if not data or not data.get('user_id'):
        return jsonify({"error": "User ID required"}), 400
    
    user_id = data['user_id']
    
    post = Post.find_by_id(post_id)
    user = User.find_by_id(user_id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        Post.add_like(post_id, user_id)
        return jsonify({"message": "Post liked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>/like", methods=["DELETE"])
def unlike_post(post_id):
    data = request.json
    if not data or not data.get('user_id'):
        return jsonify({"error": "User ID required"}), 400
    
    user_id = data['user_id']
    
    post = Post.find_by_id(post_id)
    user = User.find_by_id(user_id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        Post.remove_like(post_id, user_id)
        return jsonify({"message": "Post unliked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Comment routes
@app.route("/comments", methods=["GET"])
def get_comments():
    comments = Comment.find_all()
    return jsonify([node_to_dict(comment) for comment in comments])

@app.route("/comments/<comment_id>", methods=["GET"])
def get_comment(comment_id):
    comment = Comment.find_by_id(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    return jsonify(node_to_dict(comment))

@app.route("/comments/<comment_id>", methods=["PUT"])
def update_comment(comment_id):
    data = request.json
    if not data or not data.get('content'):
        return jsonify({"error": "Content is required"}), 400
    
    comment = Comment.find_by_id(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    try:
        updated_comment = Comment.update(comment_id, content=data['content'])
        return jsonify(node_to_dict(updated_comment))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.find_by_id(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    try:
        Comment.delete(comment_id)
        return jsonify({"message": "Comment deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>/comments", methods=["GET"])
def get_post_comments(post_id):
    post = Post.find_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    try:
        comments = Comment.find_by_post(post_id)
        return jsonify([node_to_dict(comment) for comment in comments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/posts/<post_id>/comments", methods=["POST"])
def create_comment(post_id):
    data = request.json
    if not data or not data.get('content') or not data.get('user_id'):
        return jsonify({"error": "Content and user_id required"}), 400
    
    post = Post.find_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    user = User.find_by_id(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Crée un commentaire en utilisant les IDs utilisateur et post
        comment = Comment(content=data['content'],
                          user_id=data['user_id'],
                          post_id=post_id).save()
        return jsonify(node_to_dict(comment)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/comments/<comment_id>/like", methods=["POST"])
def like_comment(comment_id):
    data = request.json
    if not data or not data.get('user_id'):
        return jsonify({"error": "User ID required"}), 400
    
    user_id = data['user_id']
    
    comment = Comment.find_by_id(comment_id)
    user = User.find_by_id(user_id)
    
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        Comment.add_like(comment_id, user_id)
        return jsonify({"message": "Comment liked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/comments/<comment_id>/like", methods=["DELETE"])
def unlike_comment(comment_id):
    data = request.json
    if not data or not data.get('user_id'):
        return jsonify({"error": "User ID required"}), 400
    
    user_id = data['user_id']
    
    comment = Comment.find_by_id(comment_id)
    user = User.find_by_id(user_id)
    
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        Comment.remove_like(comment_id, user_id)
        return jsonify({"message": "Comment unliked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

