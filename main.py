from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory


app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Flutter frontend

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    pdf_filename = db.Column(db.String(200), nullable=True)

# Initialize Database
with app.app_context():
    db.create_all()

# To-Do List Routes
@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'POST':
        data = request.json
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
        new_message = Message(forum_id=forum_id, content=data['content'])
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'message': 'Message sent'}), 201
    messages = Message.query.filter_by(forum_id=forum_id).all()
    return jsonify([{'id': msg.id, 'content': msg.content} for msg in messages])

# Notes Organizer Routes
@app.route('/notes', methods=['GET', 'POST'])
def manage_notes():
    if request.method == 'POST':
        # If a file is uploaded, expect multipart/form-data
        if 'file' in request.files:
            file = request.files['file']
            title = request.form.get('title', 'Untitled')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_note = Note(title=title, pdf_filename=filename)
                db.session.add(new_note)
                db.session.commit()
                return jsonify({'message': 'Note with PDF added'}), 201
            else:
                return jsonify({'error': 'Invalid file format'}), 400
        else:
            # Otherwise, handle JSON note submission
            data = request.json
            new_note = Note(title=data['title'])
            db.session.add(new_note)
            db.session.commit()
            return jsonify({'message': 'Note added'}), 201
    notes = Note.query.all()
    return jsonify([{'id': note.id, 'title': note.title, 'pdf_filename': note.pdf_filename} for note in notes])

@app.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = Note.query.get(id)
    if note:
        # Optionally, remove the file from disk if it exists
        if note.pdf_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.pdf_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': 'Note deleted'})
    return jsonify({'error': 'Note not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
