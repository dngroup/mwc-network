from flask import Flask
from flask import Response
from flask import request

app = Flask(__name__)

def generate(chunk_size, chunk_count):
        chunk = ''.join([str(0) for i in range(0, chunk_size)])
        n = 0
        while n < chunk_count:
            n += 1
            yield chunk


@app.route('/data')
def generate_large_csv():
    chunk_size = int(request.args.get('chunk_size'))
    chunk_count = int(request.args.get('chunk_count'))
    return Response(generate(chunk_size, chunk_count), mimetype='application/octet-stream')


if __name__ == "__main__":
    app.run()
