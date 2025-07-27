from flask import Flask, request, render_template, redirect
import boto3
import uuid
import json
import os

app = Flask(__name__)

S3_BUCKET = 'petpost-uploads-kevin'
S3_REGION = 'us-east-2'
DATA_FILE = 'pets.json'

s3 = boto3.client('s3')

# Load pets from JSON file
def load_pets():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save pets to JSON file
def save_pets(pets):
    with open(DATA_FILE, 'w') as f:
        json.dump(pets, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    pets = load_pets()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        breed = request.form['breed']
        image = request.files['image']

        # Upload image to S3
        image_filename = f"{uuid.uuid4()}_{image.filename}"
        s3.upload_fileobj(image, S3_BUCKET, image_filename)
        image_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{image_filename}"

        pet = {
            'name': name,
            'age': age,
            'breed': breed,
            'image_url': image_url
        }
        pets.append(pet)
        save_pets(pets)

        return redirect('/')

    return render_template('index.html', pets=pets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
