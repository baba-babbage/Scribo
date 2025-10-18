from flask import Flask, request, redirect, session
import os
from dotenv import load_dotenv

# Load environment variables (for password)
load_dotenv()
PASSWORD = os.getenv("NOTEBOOK_PASSWORD", "kamikaze")  # fallback to 'yash123'

app = Flask(__name__)
app.secret_key = "bhbkhabsdhbcahbdchjbasdjhcbkhabdschjbakdshbckjhabsdckjhbhkb"  # Change this to a secure random string

# Create 'notes' directory if it doesn't exist
if not os.path.exists("notes"):
    os.makedirs("notes")

# Home/Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect("/notes")
    return '''
      <h1> SCRIBO </H2>
        <h2>🔐 Login</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter password">
            <button type="submit">Login</button>
        </form>
    '''

# Notes list with search, creation, deletion, and renaming
@app.route("/notes", methods=["GET", "POST"])
def notes():
    if not session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":
        action = request.form.get("action")
        filename = request.form.get("filename")
        if action == "create" and filename:
            filename = filename if filename.endswith(".txt") else filename + ".txt"
            open(os.path.join("notes", filename), "w").close()
        elif action == "delete" and filename:
            os.remove(os.path.join("notes", filename))
        elif action == "rename":
            old_name = request.form.get("old_name")
            new_name = request.form.get("new_name")
            if old_name and new_name:
                os.rename(os.path.join("notes", old_name), os.path.join("notes", new_name))
        return redirect("/notes")

    files = os.listdir("notes")
    file_links = ''.join(
        f'<li>{file} '
        f'<a href="/note/{file}">📝</a> '
        f'<form style="display:inline;" method="POST"><input type="hidden" name="action" value="delete"><input type="hidden" name="filename" value="{file}"><button type="submit">🗑️</button></form>'
        f'<form style="display:inline;" method="POST">'
        f'<input type="hidden" name="action" value="rename">'
        f'<input type="hidden" name="old_name" value="{file}">'
        f'<input name="new_name" placeholder="Rename to" required>'
        f'<button type="submit">✏️</button></form>'
        f'</li>' for file in files)

    return f'''
        <html><body style="background-color:#f4f4f4; color:#333; font-family:sans-serif; padding:20px;">
        <h1> SCRIBO </H1>
        <h2>📒 Your Notes</h2>
        <form method="POST">
            <input type="hidden" name="action" value="create">
            <input name="filename" placeholder="New note name" required>
            <button type="submit">Create</button>
        </form>
        <br>
        <input type="text" id="search" placeholder="Search notes..." onkeyup="filterNotes()">
        <ul id="noteList">
            {file_links}
        </ul>
        <a href="/logout">Logout</a>
        <script>
            function filterNotes() {{
                let input = document.getElementById("search").value.toLowerCase();
                let notes = document.getElementById("noteList").getElementsByTagName("li");
                for (let note of notes) {{
                    note.style.display = note.textContent.toLowerCase().includes(input) ? "" : "none";
                }}
            }}
        </script>
        </body></html>
    '''

# Edit individual note with Quill rich text editor
@app.route("/note/<filename>", methods=["GET", "POST"])
def edit_note(filename):
    if not session.get("logged_in"):
        return redirect("/")

    filepath = os.path.join("notes", filename)
    if request.method == "POST":
        content = request.form.get("note")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    content = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

    return f"""
    <html>
      <head>
        <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
        <style>
          body {{
            background-color: #1e1e1e;
            color: #f1f1f1;
            font-family: sans-serif;
            padding: 20px;
          }}
          #editor {{
            height: 500px;
            background-color: white;
            color: black;
          }}
          .ql-editor {{
            color: black;
          }}
        </style>
      </head>
      <body>
      <h1> SCRIBO </H1>
        <h2>📝 Editing: {filename}</h2>
        <form method="POST" onsubmit="saveContent()">
          <input type="hidden" name="note" id="note-input">
          <div id="editor">{content}</div>
          <br>
          <button type="submit">💾 Save</button>
        </form>
        <a href="/notes">← Back to Notes</a>

        <script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>
        <script>
          var quill = new Quill('#editor', {{
            theme: 'snow',
            modules: {{
              toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                ['blockquote', 'code-block'],
                [{{ 'header': 1 }}, {{ 'header': 2 }}],
                [{{ 'list': 'ordered'}}, {{ 'list': 'bullet' }}],
                [{{ 'color': [] }}, {{ 'background': [] }}],
                ['clean']
              ]
            }}
          }});

          function saveContent() {{
            var note = document.querySelector('input[name=note]');
            note.value = document.querySelector('.ql-editor').innerHTML;
          }}
        </script>
      </body>
    </html>
    """

# Logout route
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)