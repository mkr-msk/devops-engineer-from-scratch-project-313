import json
import os
import subprocess

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, redirect, request
from flask_cors import CORS
from pydantic import ValidationError
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from database import engine
from models import Link
from schemas import LinkCreate, LinkUpdate

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

# Run database migrations on startup
try:
    subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True)
    print("Database migrations applied successfully")
except subprocess.CalledProcessError as e:
    print(f"Warning: Migration failed: {e.stderr.decode()}")

app = Flask(__name__)

if os.getenv("DEBUG"):
    CORS(
        app,
        origins=["http://localhost:5173"],
        methods=["GET", "POST", "PUT", "DELETE"],
    )

# SENTRY
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment="production",
    )


def format_link_response(link: Link) -> dict:
    return {
        "id": link.id,
        "original_url": link.original_url,
        "short_name": link.short_name,
        "short_url": f"{BASE_URL}/r/{link.short_name}",
        "created_at": link.created_at.isoformat(),
    }


# HEALTH CHECK
@app.route("/ping")
def ping():
    return "pong"


# CRUD
@app.route("/api/links", methods=["GET"])
def get_links():
    with Session(engine) as session:
        range_param = request.args.get("range")
        statement = select(Link)
        total_count = session.exec(select(func.count()).select_from(Link)).one()

        if range_param:
            try:
                range_str = range_param.strip("[]").replace(" ", "")
                start, end = map(int, range_str.split(","))

                if start < 0 or end < 0:
                    return jsonify({"detail": "Range values must be non-negative"}), 400

                if start > end:
                    return jsonify({"detail": "Range start must be less than end"}), 400

                offset = start
                limit = end - start + 1
                statement = statement.offset(offset).limit(limit)
                links = session.exec(statement).all()
                actual_end = start + len(links)

                response = make_response(
                    jsonify([format_link_response(link) for link in links])
                )

                if len(links) > 0:
                    response.headers["Content-Range"] = (
                        f"links {start + 1}-{actual_end}/{total_count}"  # noqa: E501
                    )
                else:
                    response.headers["Content-Range"] = f"links */{total_count}"

                return response, 200

            except (ValueError, AttributeError):
                detail = (
                    f"Invalid range format. "
                    f"Expected [start,end], got: {range_param}"
                )
                return jsonify({"detail": detail}), 400

        links = session.exec(statement).all()
        response = make_response(
            jsonify([format_link_response(link) for link in links])
        )

        if total_count > 0:
            response.headers["Content-Range"] = f"links 1-{total_count}/{total_count}"
        else:
            response.headers["Content-Range"] = f"links */{total_count}"

        return response, 200


@app.route("/api/links", methods=["POST"])
def create_link():
    try:
        data = request.get_json()
        link_data = LinkCreate(**data)

        with Session(engine) as session:
            link_dict = link_data.model_dump(mode="json")
            new_link = Link(**link_dict)
            session.add(new_link)
            session.commit()
            session.refresh(new_link)

            return jsonify(format_link_response(new_link)), 201

    except ValidationError as e:
        # Parse JSON string to ensure it's JSON-serializable
        errors = json.loads(e.json())
        # Add "body" prefix to loc array to match FastAPI format
        for error in errors:
            if "loc" in error:
                error["loc"] = ["body"] + list(error["loc"])
        return jsonify({"detail": errors}), 422

    except IntegrityError:
        return jsonify(
            {"detail": f'Short name "{data.get("short_name")}" already exists'}
        ), 409

    except ValueError as e:
        return jsonify({"detail": str(e)}), 422

    except Exception as e:
        app.logger.error(f"Error creating link: {e}", exc_info=True)
        return jsonify({"detail": "An error occured while creating the link"}), 500


@app.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id: int):
    with Session(engine) as session:
        link = session.get(Link, link_id)

        if not link:
            return jsonify({"detail": f"Link with id {link_id} not found"}), 404

        return jsonify(format_link_response(link)), 200


@app.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id: int):
    try:
        data = request.get_json()
        update_data = LinkUpdate(**data)

        with Session(engine) as session:
            link = session.get(Link, link_id)

            if not link:
                return jsonify({"detail": f"Link with id {link_id} not found"}), 404

            update_dict = update_data.model_dump(exclude_unset=True, mode="json")
            for key, value in update_dict.items():
                setattr(link, key, value)

            session.add(link)
            session.commit()
            session.refresh(link)

            return jsonify(format_link_response(link)), 200

    except ValidationError as e:
        # Parse JSON string to ensure it's JSON-serializable
        errors = json.loads(e.json())
        # Add "body" prefix to loc array to match FastAPI format
        for error in errors:
            if "loc" in error:
                error["loc"] = ["body"] + list(error["loc"])
        return jsonify({"detail": errors}), 422

    except IntegrityError:
        return jsonify(
            {"detail": f'Short name "{data.get("short_name")}" already exists'}
        ), 409

    except TypeError as e:
        return jsonify({"detail": [{"msg": str(e), "type": "type_error"}]}), 422

    except ValueError as e:
        return jsonify({"detail": str(e)}), 422

    except Exception as e:
        app.logger.error(f"Error creating link: {e}", exc_info=True)
        return jsonify({"detail": "An error occured while creating the link"}), 500


@app.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id: int):
    with Session(engine) as session:
        link = session.get(Link, link_id)

        if not link:
            return jsonify({"detail": f"Link with id {link_id} not found"}), 404

        session.delete(link)
        session.commit()

        return "", 204


# REDIRECT
@app.route("/r/<short_name>")
def redirect_to_original(short_name: str):
    with Session(engine) as session:
        statement = select(Link).where(Link.short_name == short_name)
        link = session.exec(statement).first()

        if not link:
            return jsonify({"detail": f"Short link {short_name} not found"}), 404

    return redirect(link.original_url, code=301)


# ERRORS
@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "The requested URL was not found on the server."}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"detail": "An unexpected error occurred."}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(f"Unhandled exception: {error}", exc_info=True)

    return jsonify({"detail": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
