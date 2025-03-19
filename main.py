from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Flutter frontend

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Define Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# To-Do List Routes
@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'POST':
        data = request.json
        # Expecting JSON: { "title": "Task title" }
        new_task = Task(title=data['title'])
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task added'}), 201
    tasks = Task.query.all()
    return jsonify([{'id': task.id, 'title': task.title} for task in tasks])

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404

# Discussion Forum Routes
@app.route('/forums', methods=['GET', 'POST'])
def manage_forums():
    if request.method == 'POST':
        data = request.json
        # Expecting JSON: { "name": "Forum name" }
        new_forum = Forum(name=data['name'])
        db.session.add(new_forum)
        db.session.commit()
        return jsonify({'message': 'Forum created'}), 201
    forums = Forum.query.all()
    return jsonify([{'id': forum.id, 'name': forum.name} for forum in forums])

@app.route('/forums/<int:forum_id>/messages', methods=['GET', 'POST'])
def manage_messages(forum_id):
    if request.method == 'POST':
        data = request.json
        # Expecting JSON: { "content": "Message content" }
        new_message = Message(forum_id=forum_id, content=data['content'])
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'message': 'Message sent'}), 201
    messages = Message.query.filter_by(forum_id=forum_id).all()
    return jsonify([{'id': msg.id, 'content': msg.content} for msg in messages])

if __name__ == '__main__':
    app.run(debug=True)
