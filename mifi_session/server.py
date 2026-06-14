from flask import Flask, request, jsonify
import pickle
import numpy as np
import threading
import pika
import json
import uuid

with open('models/tree.pkl', 'rb') as pkl_file:
    model = pickle.load(pkl_file)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Test message. The server is running'


def process_and_publish(features_list, task_id):
    """Фоновая задача: считает модель и отправляет результат в RabbitMQ"""
    try:
        features_array = np.array(features_list).reshape(1, -1)
        prediction = int(model.predict(features_array)[0])
        probability = float(model.predict_proba(features_array)[0][1])

        result_payload = {
            "task_id": task_id,
            "prediction": prediction,
            "probability": probability,
            "status": "completed"
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='ml_results', durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='ml_results',
            body=json.dumps(result_payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Error in background worker: {e}", flush=True)

@app.route('/predict', methods=['POST'])
def predict():
    """
        Выполняет и возвращает прогноз и вероятность.

        Ожидаемые параметры (JSON):
        Массив из 24 чисел.
        Пример: [5.1, 3.5, 1.4, 0.2, ...]

        Возвращаемая структура (JSON):
        Прогноз и вероятность в виде float-чисел.
        Пример: {"prediction": 1.0}
    """

    features = request.json

    if features is None:
        return jsonify({'error': 'No data provided'}), 400

    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=process_and_publish, args=(features, task_id))
    thread.start()

    return jsonify({
        'status': 'accepted',
        'task_id': task_id,
        'message': 'Выполняется обучение.'
    }), 202

@app.route('/health')
def health():
    """
        Проверяет работоспособность приложения.

        Ожидаемые параметры (JSON):
        Возвращает статус приложения.
        Пример: {"status": "healthy"}
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)