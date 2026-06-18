"""Головний файл Flask-додатка."""

from importlib import metadata

from flask import Flask, jsonify, request

from config import config_by_name


def create_app(config_name: str = "default") -> Flask:
    """Фабрика додатка Flask.

    Args:
        config_name: ім'я конфігурації ('development', 'production').

    Returns:
        Налаштований екземпляр Flask.
    """
    app = Flask(__name__)

    selected_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(selected_config)

    register_routes(app)

    return app


def get_flask_version() -> str:
    """Повертає встановлену версію Flask."""
    try:
        return metadata.version("Flask")
    except metadata.PackageNotFoundError:
        return "невідома"


def register_routes(app: Flask) -> None:
    """Реєструє маршрути додатка."""

    @app.route("/")
    def index():
        """Головна сторінка."""
        return """
        <!doctype html>
        <html lang="uk">
        <head>
            <meta charset="utf-8">
            <title>Flask-проект</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <h1>Головна сторінка Flask-проекту</h1>
            <p>Це мінімальний Flask-додаток з маршрутизацією.</p>
            <ul>
                <li><a href="/about">Про додаток</a></li>
                <li><a href="/api/info">API info</a></li>
                <li><a href="/greet/Олена">Привітання</a></li>
            </ul>
        </body>
        </html>
        """

    @app.route("/about")
    def about():
        """Сторінка 'Про додаток'."""
        return """
        <!doctype html>
        <html lang="uk">
        <head>
            <meta charset="utf-8">
            <title>Про Flask-проект</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <h1>Про додаток</h1>
            <p>Цей проект демонструє Application Factory, конфігурацію та маршрути Flask.</p>
            <p><a href="/">На головну</a></p>
        </body>
        </html>
        """

    @app.route("/api/info")
    def api_info():
        """API-ендпоінт з інформацією у JSON."""
        routes = sorted(str(rule) for rule in app.url_map.iter_rules())
        return jsonify(
            {
                "framework": "Flask",
                "version": get_flask_version(),
                "debug": app.config["DEBUG"],
                "routes": routes,
            }
        )

    @app.route("/greet")
    @app.route("/greet/<name>")
    def greet(name=None):
        """Маршрут з динамічним параметром та query-параметром."""
        user_name = name or request.args.get("name", "Гість")
        return f"<h1>Вітаємо, {user_name}!</h1><p><a href='/'>На головну</a></p>"


if __name__ == "__main__":
    application = create_app("development")
    application.run(debug=application.config["DEBUG"], port=5000)
