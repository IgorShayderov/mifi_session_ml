from flask import Flask
import pickle

with open('models/model.pkl', 'rb') as pkl_file:
    model = pickle.load(pkl_file)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Privet'

@app.route('/predict', methods=['POST'])
def predict():
    return None

@app.route('/heath')
def health():
    return None

if __name__ == '__main__':
    app.run('localhost', 5001)
