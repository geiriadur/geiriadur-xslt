from flask import Flask

app = Flask(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

from flask import request

@app.route("/")
def call_script():
    import subprocess

    name = request.args.get("name") or next(iter(request.args.keys()), "")

    result = subprocess.run(
        #["python3", "dictionary.py", name],   # or any command
        ["python3", "dictionary.py", request.query_string.decode()],
        capture_output=True,
        text=True
    )

    output = result.stdout
    #print(output) # Prints output (for testing on server)
    return output # Returns output as server response
