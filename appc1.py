from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_professor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # video, audio, image, text
    description = db.Column(db.String(200), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize Database
db.create_all()

# Routes for Course Management
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': course.id, 'title': course.title, 'description': course.description} for course in courses])

@app.route('/courses', methods=['POST'])
def add_course():
    data = request.json
    new_course = Course(title=data['title'], description=data['description'])
    db.session.add(new_course)
    db.session.commit()
    return jsonify({'message': 'Course added successfully!'}), 201

@app.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.json
    course.title = data['title']
    course.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Course updated successfully!'})

@app.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted successfully!'})

# Routes for Student Chat
@app.route('/courses/<int:course_id>/messages', methods=['GET'])
def get_messages(course_id):
    messages = Message.query.filter_by(course_id=course_id).all()
    return jsonify([{'id': msg.id, 'student_name': msg.student_name, 'content': msg.content, 'response': msg.response} for msg in messages])

@app.route('/courses/<int:course_id>/messages', methods=['POST'])
def add_message(course_id):
    data = request.json
    new_message = Message(student_name=data['student_name'], content=data['content'], course_id=course_id)
    db.session.add(new_message)
    db.session.commit()
    # Placeholder for AI-generated response
    response = f"This is a response to: {data['content']}"
    new_message.response = response
    db.session.commit()
    return jsonify({'message': 'Message added successfully!', 'response': response}), 201

# Routes for Useful Links
@app.route('/courses/<int:course_id>/links', methods=['GET'])
def get_links(course_id):
    links = Link.query.filter_by(course_id=course_id).all()
    return jsonify([{'id': link.id, 'url': link.url, 'type': link.type, 'description': link.description} for link in links])

@app.route('/courses/<int:course_id>/links', methods=['POST'])
def add_link(course_id):
    data = request.json
    new_link = Link(url=data['url'], type=data['type'], description=data['description'], course_id=course_id)
    db.session.add(new_link)
    db.session.commit()
    return jsonify({'message': 'Link added successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
