from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret_key'

# Simulated user DB
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "user": {"password": "user123", "role": "User"}
}

# ✅ FIXED ABSOLUTE PATH
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        user = users.get(username)
        if user and user["password"] == password and user["role"] == role:
            session["username"] = username
            session["role"] = role
            flash(f"Welcome {role} ({username})", "success")
            return redirect(url_for("upload"))
        else:
            flash("Invalid username, password, or role.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if username in users:
            flash("Username already exists.", "warning")
            return redirect(url_for("register"))

        users[username] = {"password": password, "role": role}
        flash("Registered successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    username = session["username"]
    role = session["role"]

    if request.method == "POST":
        file = request.files.get("file")

        if file and file.filename:
            filename = secure_filename(f"{username}_{file.filename}")
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(file_path)

            session["uploaded_file"] = filename
            flash(f"File '{filename}' uploaded successfully.", "success")

            return redirect(url_for("encrypt"))
        else:
            flash("No file selected.", "warning")

    return render_template("upload.html", username=username, role=role)


@app.route("/encrypt")
def encrypt():
    if "username" not in session or "uploaded_file" not in session:
        flash("Please upload a file first.", "warning")
        return redirect(url_for("upload"))

    username = session["username"]
    filename = session["uploaded_file"]

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Encrypt
    encrypted_data = hybrid_encrypt(file_path)

    encrypted_filename = filename + ".enc"
    encrypted_path = os.path.join(app.config["UPLOAD_FOLDER"], encrypted_filename)

    # ✅ FIXED WRITE
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data.encode())

    session["encrypted_file"] = encrypted_filename

    flash("File encrypted successfully.", "success")

    return render_template(
        "encrypt.html",
        username=username,
        filename=filename,
        encrypted_filename=encrypted_filename,
        result=encrypted_data
    )


# ✅ FINAL WORKING DOWNLOAD
@app.route("/download/<path:filename>")
def download(filename):
    upload_folder = app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    print("Downloading:", file_path)  # debug

    if not os.path.exists(file_path):
        return f"File not found: {file_path}", 404

    return send_from_directory(
        directory=upload_folder,
        path=filename,
        as_attachment=True
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# Dummy encryption
def hybrid_encrypt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    return "Encrypted:\n" + ''.join(format(ord(c), '08b') for c in content)


if __name__ == "__main__":
    app.run(debug=True)