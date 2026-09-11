from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'evidencias.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
db = SQLAlchemy(app)


class Evidence(db.Model):
    """Registro de uma aula e seu arquivo comprobatório."""

    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(120), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False)
    bimester = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_upload_name(original_name):
    safe_name = secure_filename(original_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{uuid4().hex[:8]}_{safe_name}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form = request.form
        required_fields = [
            form.get("teacher_name", "").strip(),
            form.get("subject", "").strip(),
            form.get("class_name", "").strip(),
            form.get("lesson_date", "").strip(),
            form.get("bimester", "").strip(),
            form.get("description", "").strip(),
        ]
        uploaded_file = request.files.get("evidence_file")

        if not all(required_fields) or not uploaded_file or not uploaded_file.filename:
            flash("Preencha todos os campos obrigatórios e anexe uma evidência.", "danger")
            return redirect(url_for("index"))
        if not allowed_file(uploaded_file.filename):
            flash("Formato inválido. Envie uma imagem JPG, PNG ou um PDF.", "danger")
            return redirect(url_for("index"))

        try:
            lesson_date = date.fromisoformat(form["lesson_date"])
        except ValueError:
            flash("Informe uma data de aula válida.", "danger")
            return redirect(url_for("index"))

        filename = build_upload_name(uploaded_file.filename)
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        uploaded_file.save(UPLOAD_FOLDER / filename)
        evidence = Evidence(
            teacher_name=form["teacher_name"].strip(), subject=form["subject"].strip(),
            class_name=form["class_name"].strip(), lesson_date=lesson_date,
            bimester=form["bimester"], description=form["description"].strip(), filename=filename,
        )
        db.session.add(evidence)
        db.session.commit()
        flash("Evidência registrada com sucesso.", "success")
        return redirect(url_for("index"))

    evidences = Evidence.query.order_by(Evidence.lesson_date.desc(), Evidence.created_at.desc()).all()
    return render_template("index.html", evidences=evidences)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.context_processor
def inject_helpers():
    def is_image(filename):
        return filename.rsplit(".", 1)[-1].lower() in {"jpg", "jpeg", "png"}

    return {"is_image": is_image}


with app.app_context():
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)