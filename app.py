from flask import Flask, request
from cache import cache
from ithaka_service import IthakaService
app = Flask(__name__)
cache.init_app(app)


@app.route("/")
def health_check():
    return "Healthy server!"


@app.route("/lazy_jack", methods=['POST'])
def lazy_jack():
    return IthakaService.get_preferred_route(request.get_json())


@app.route("/clear_cache")
def clear_cache():
    cache.clear()
    return {}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
