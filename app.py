from __future__ import annotations

import csv
import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
IMAGE_DIR = STATIC_DIR / "images"
PROJECT_IMAGE_DIR = IMAGE_DIR / "projects"
CERT_IMAGE_DIR = IMAGE_DIR / "certificates"
ACHIEVEMENT_IMAGE_DIR = IMAGE_DIR / "achievements"
DATABASE_PATH = BASE_DIR / "database.db"
CONTACTS_FILE = DATA_DIR / "contacts.csv"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "portfolio-dev-secret")
app.config["DATABASE"] = DATABASE_PATH
app.config["UPLOAD_FOLDER"] = PROJECT_IMAGE_DIR
app.config["ADMIN_USERNAME"] = os.environ.get("ADMIN_USERNAME", "Rohan")
app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash(
    os.environ.get("ADMIN_PASSWORD", "Rohan@2005")
)

DEFAULT_SETTINGS = {
    "name": "Rohan Dalve",
    "role": "Data Analyst & Machine Learning Enthusiast",
    "tagline": "Turning raw data into strategic insight, decision-ready dashboards, and practical machine learning solutions.",
    "email": "dalverohan722@gmail.com",
    "phone": "+91 7972042722",
    "github": "https://github.com/Rohan-dalve",
    "linkedin": "https://www.linkedin.com/in/rohan-dalve/",
    "location": "Pune, Maharashtra, India",
    "resume_highlight_1": "MCA background with hands-on internship experience in analytics and reporting.",
    "resume_highlight_2": "Strong working knowledge of Python, SQL, Power BI, Excel, and dashboard-driven analysis.",
    "resume_highlight_3": "Focused on machine learning, data storytelling, and practical Flask-based solutions.",
    "github_section_title": "GitHub Highlights",
    "github_section_text": "Explore my GitHub profile to review portfolio projects, practice work, and real implementation-focused analytics projects.",
}

DEFAULT_ABOUT = (
    "I am an MCA student and aspiring data professional with internship experience as a Data Analyst Intern. "
    "My work combines Python, SQL, Power BI, and Excel with practical machine learning knowledge in regression "
    "and classification. I enjoy building data-driven solutions that turn raw information into clear insights, "
    "interactive dashboards, and useful decision-support applications."
)

DEFAULT_SKILLS = [
    ("Python", 90),
    ("SQL", 85),
    ("Power BI", 88),
    ("Excel", 87),
    ("Pandas", 89),
    ("NumPy", 85),
    ("Scikit-learn", 84),
    ("Matplotlib", 80),
    ("Seaborn", 78),
    ("Flask", 82),
]

DEFAULT_SERVICES = [
    ("Data Cleaning", "Preparing raw and inconsistent datasets for accurate analysis and reporting."),
    ("Data Visualization", "Designing clear visuals and dashboards that make patterns easy to understand."),
    ("Machine Learning Models", "Applying regression and classification methods to solve practical problems."),
    ("Dashboard Development", "Building KPI-focused dashboards in Power BI for faster decision-making."),
]

DEFAULT_TOOLS = ["Python", "SQL", "Power BI", "Excel", "Flask", "Git"]
DEFAULT_LEARNING = ["Advanced Machine Learning", "Data Engineering Fundamentals"]

DEFAULT_PROJECTS = [
    {
        "title": "Loan Prediction Web App",
        "description": "A Flask-based machine learning application that predicts loan approval outcomes through an easy-to-use web interface.",
        "tech_stack": "Flask, Machine Learning, Scikit-learn, SQLite, Python",
        "github_link": "https://github.com/Rohan-dalve",
        "problem_statement": "Loan approval analysis can be slow and inconsistent when screening is done manually without a data-backed predictive process.",
        "approach": "I cleaned the dataset, handled preprocessing and feature preparation, trained a classification model, and integrated it into a Flask web application for real-time predictions.",
        "impact": "The project demonstrates how machine learning can support faster and more consistent preliminary loan evaluation through an accessible web workflow.",
    },
    {
        "title": "Customer Purchase Analysis",
        "description": "A dashboard-focused analytics project that studies customer behavior, revenue trends, and product performance using SQL, Power BI, and Python.",
        "tech_stack": "SQL, Power BI, Python",
        "github_link": "https://github.com/Rohan-dalve",
        "problem_statement": "Businesses often lack a clear view of which customer segments, products, and patterns actually drive revenue and retention.",
        "approach": "I analyzed transactional data with SQL and Python, then created interactive Power BI dashboards to highlight revenue trends, product performance, and customer segmentation insights.",
        "impact": "The final dashboard helps decision-makers understand revenue drivers and identify opportunities to improve customer retention and sales strategy.",
    },
]

DEFAULT_EXPERIENCE = [
    {
        "title": "Data Analyst Intern",
        "company": "3SV Software Solutions",
        "location": "Pune",
        "duration": "Jan 2025 - Mar 2025",
        "highlights": [
            "Analyzed structured business data using SQL and Excel for reporting and validation tasks.",
            "Supported Power BI dashboard development for KPI monitoring and trend analysis.",
            "Improved data quality through cleaning and preprocessing workflows.",
            "Contributed analytical support for data-driven operational decisions.",
        ],
    }
]

DEFAULT_ACHIEVEMENTS = [
    "Student Association President with experience leading initiatives and coordinating teams.",
    "Focused on combining technical analytics skills with communication, leadership, and ownership.",
]


def ensure_directories() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    IMAGE_DIR.mkdir(exist_ok=True)
    PROJECT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    CERT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    ACHIEVEMENT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_contacts_file() -> None:
    ensure_directories()
    if CONTACTS_FILE.exists():
        return

    with CONTACTS_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "name", "email", "subject", "message"])


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    return get_db().execute(query, params).fetchall()


def query_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    return get_db().execute(query, params).fetchone()


def ensure_column(db: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    existing_columns = {row[1] for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in existing_columns:
        db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_project_image(uploaded_file) -> str | None:
    if not uploaded_file or not uploaded_file.filename:
        return None
    if not allowed_image(uploaded_file.filename):
        return None

    safe_name = secure_filename(uploaded_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{safe_name}"
    destination = PROJECT_IMAGE_DIR / filename
    uploaded_file.save(destination)
    return f"images/projects/{filename}"


def save_profile_image(uploaded_file) -> bool:
    if not uploaded_file or not uploaded_file.filename:
        return False
    if not allowed_image(uploaded_file.filename):
        return False

    uploaded_file.save(IMAGE_DIR / "profile.jpg")
    return True


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin dashboard.", "error")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def init_database() -> None:
    ensure_directories()
    db = sqlite3.connect(app.config["DATABASE"])

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            image TEXT,
            github_link TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS about (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level INTEGER NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            employment_type TEXT,
            start_date TEXT,
            end_date TEXT,
            current_job INTEGER DEFAULT 0,
            location TEXT,
            description TEXT,
            responsibilities TEXT,
            technologies TEXT,
            display_order INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issuer TEXT,
            issue_date TEXT,
            credential_id TEXT,
            verification_url TEXT,
            image TEXT,
            category TEXT,
            description TEXT,
            display_order INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            organization TEXT,
            achievement_date TEXT,
            description TEXT,
            image TEXT,
            display_order INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT
        )
        """
    )

    ensure_column(db, "projects", "problem_statement", "TEXT")
    ensure_column(db, "projects", "approach", "TEXT")
    ensure_column(db, "projects", "impact", "TEXT")

    for key, value in DEFAULT_SETTINGS.items():
        db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    if db.execute("SELECT COUNT(*) FROM about").fetchone()[0] == 0:
        db.execute("INSERT INTO about (content) VALUES (?)", (DEFAULT_ABOUT,))

    if db.execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 0:
        db.executemany("INSERT INTO skills (name, level) VALUES (?, ?)", DEFAULT_SKILLS)

    if db.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        db.executemany("INSERT INTO services (title, description) VALUES (?, ?)", DEFAULT_SERVICES)

    if db.execute("SELECT COUNT(*) FROM tools").fetchone()[0] == 0:
        db.executemany("INSERT INTO tools (name) VALUES (?)", [(tool,) for tool in DEFAULT_TOOLS])

    if db.execute("SELECT COUNT(*) FROM learning").fetchone()[0] == 0:
        db.executemany("INSERT INTO learning (title) VALUES (?)", [(item,) for item in DEFAULT_LEARNING])

    if db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
        for project in DEFAULT_PROJECTS:
            db.execute(
                """
                INSERT INTO projects (title, description, tech_stack, image, github_link, problem_statement, approach, impact)
                VALUES (?, ?, ?, NULL, ?, ?, ?, ?)
                """,
                (
                    project["title"],
                    project["description"],
                    project["tech_stack"],
                    project["github_link"],
                    project["problem_statement"],
                    project["approach"],
                    project["impact"],
                ),
            )

    db.commit()
    db.close()


def get_settings_dict() -> dict[str, str]:
    settings = DEFAULT_SETTINGS.copy()
    rows = query_all("SELECT key, value FROM settings")
    settings.update({row["key"]: row["value"] for row in rows})
    return settings


def normalize_text(value: str) -> str:
    return value.strip().lower()


def build_skill_categories(skills: list[sqlite3.Row], tools: list[sqlite3.Row]) -> list[dict[str, object]]:
    categories = [
        {
            "name": "Programming",
            "icon": "</>",
            "keywords": ["python", "sql", "git", "javascript", "java", "c ", "c++", "c#"],
            "items": [],
        },
        {
            "name": "Data Analytics",
            "icon": "📊",
            "keywords": ["power bi", "excel", "pandas", "tableau", "analytics", "data"],
            "items": [],
        },
        {
            "name": "Machine Learning",
            "icon": "🤖",
            "keywords": ["scikit", "numpy", "matplotlib", "seaborn", "tensorflow", "keras", "pytorch", "machine learning", "ml"],
            "items": [],
        },
        {
            "name": "Web Development",
            "icon": "🌐",
            "keywords": ["flask", "html", "css", "javascript", "bootstrap", "react", "django", "web"],
            "items": [],
        },
    ]

    combined = []
    seen = set()
    for row in skills + tools:
        name = row["name"].strip()
        key = normalize_text(name)
        if key in seen:
            continue
        seen.add(key)
        combined.append({"name": name, "key": key})

    for entry in combined:
        assigned = False
        for category in categories:
            if any(keyword in entry["key"] for keyword in category["keywords"]):
                category["items"].append(entry)
                assigned = True
                break
        if not assigned:
            categories[0]["items"].append(entry)

    return [category for category in categories if category["items"]]


def build_github_summary(projects: list[sqlite3.Row]) -> dict[str, object]:
    repo_count = sum(1 for project in projects if project["github_link"])
    tech_counts: dict[str, int] = {}
    keywords = [
        "python",
        "flask",
        "sql",
        "power bi",
        "excel",
        "scikit-learn",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "machine learning",
    ]
    for project in projects:
        tech_stack = normalize_text(project["tech_stack"])
        for keyword in keywords:
            if keyword in tech_stack:
                tech_counts[keyword] = tech_counts.get(keyword, 0) + 1

    top_languages = [language.title() for language, _ in sorted(tech_counts.items(), key=lambda item: (-item[1], item[0]))][:4]
    if not top_languages:
        top_languages = ["Python", "SQL", "Flask"]

    return {
        "repo_count": repo_count,
        "top_languages": top_languages,
        "project_count": len(projects),
        "contributions": min(max(repo_count * 8, 12), 48),
    }


def get_portfolio_content() -> dict:
    about_row = query_one("SELECT * FROM about ORDER BY id LIMIT 1")
    skills = query_all("SELECT * FROM skills ORDER BY level DESC, name ASC")
    projects = query_all("SELECT * FROM projects ORDER BY id DESC")
    services = query_all("SELECT * FROM services ORDER BY id ASC")
    tools = query_all("SELECT * FROM tools ORDER BY id ASC")
    learning = query_all("SELECT * FROM learning ORDER BY id ASC")
    skill_categories = build_skill_categories(skills, tools)
    github_summary = build_github_summary(projects)

    # Load dynamic content for experiences, certifications, achievements
    exp_rows = query_all("SELECT * FROM experience WHERE status = 1 ORDER BY display_order DESC, start_date DESC")
    cert_rows = query_all("SELECT * FROM certifications WHERE status = 1 ORDER BY display_order DESC, issue_date DESC")
    ach_rows = query_all("SELECT * FROM achievements WHERE status = 1 ORDER BY display_order DESC, achievement_date DESC")

    # Transform to structures expected by templates (backwards compatible)
    experience_list = []
    for r in exp_rows:
        duration = r["start_date"] or ""
        if r["current_job"]:
            duration = f"{r['start_date']} - Present" if r['start_date'] else "Present"
        else:
            duration = f"{r['start_date']} - {r['end_date']}" if r['start_date'] or r['end_date'] else ""

        highlights = [line.strip() for line in (r["responsibilities"] or "").split("\n") if line.strip()]

        experience_list.append(
            {
                "title": r["job_title"],
                "company": r["company_name"],
                "location": r["location"] or "",
                "duration": duration,
                "highlights": highlights,
                "technologies": r["technologies"] or "",
            }
        )

    certifications = [dict(title=r["title"], issuer=r["issuer"], issue_date=r["issue_date"], credential_id=r["credential_id"], verification_url=r["verification_url"], image=r["image"], category=r["category"], description=r["description"]) for r in cert_rows]
    achievements = [r["title"] for r in ach_rows]

    return {
        "site": get_settings_dict(),
        "about": about_row["content"] if about_row else "",
        "skills": skills,
        "projects": projects,
        "services": services,
        "tools": tools,
        "learning": learning,
        "experience": DEFAULT_EXPERIENCE,
        "achievements": DEFAULT_ACHIEVEMENTS,
        "skill_categories": skill_categories,
        "github_summary": github_summary,
        "experiences": exp_rows,
        "certifications": certifications,
        "achievements": achievements,
        "experience": experience_list,
    }


@app.context_processor
def inject_globals():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    db.close()
    site = DEFAULT_SETTINGS.copy()
    site.update({row["key"]: row["value"] for row in rows})
    return {"site": site, "current_year": datetime.now().year}


@app.route("/")
def home():
    return render_template("index.html", portfolio=get_portfolio_content())


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        valid_login = username == app.config["ADMIN_USERNAME"] and check_password_hash(
            app.config["ADMIN_PASSWORD_HASH"], password
        )
        if valid_login:
            session["admin_logged_in"] = True
            session["admin_username"] = username
            flash("Login successful. Welcome to your dashboard.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin_login.html")


@app.route("/logout", methods=["POST"])
@admin_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/dashboard")
@admin_required
def dashboard():
    return render_template(
        "dashboard.html",
        settings=get_settings_dict(),
        about=query_one("SELECT * FROM about ORDER BY id LIMIT 1"),
        skills=query_all("SELECT * FROM skills ORDER BY level DESC, name ASC"),
        projects=query_all("SELECT * FROM projects ORDER BY id DESC"),
        services=query_all("SELECT * FROM services ORDER BY id ASC"),
        tools=query_all("SELECT * FROM tools ORDER BY id ASC"),
        learning=query_all("SELECT * FROM learning ORDER BY id ASC"),
    )


@app.route("/update-settings", methods=["POST"])
@admin_required
def update_settings():
    fields = [
        "name",
        "role",
        "tagline",
        "email",
        "phone",
        "github",
        "linkedin",
        "location",
        "resume_highlight_1",
        "resume_highlight_2",
        "resume_highlight_3",
        "github_section_title",
        "github_section_text",
    ]
    db = get_db()
    for field in fields:
        value = request.form.get(field, "").strip()
        db.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (field, value),
        )
    db.commit()
    flash("Portfolio settings updated successfully.", "success")
    return redirect(url_for("dashboard") + "#settings-manager")


@app.route("/upload-profile-image", methods=["POST"])
@admin_required
def upload_profile_image():
    if not save_profile_image(request.files.get("profile_image")):
        flash("Please upload a valid profile image.", "error")
        return redirect(url_for("dashboard") + "#settings-manager")

    flash("Profile image updated successfully.", "success")
    return redirect(url_for("dashboard") + "#settings-manager")


@app.route("/update-about", methods=["POST"])
@admin_required
def update_about():
    content = request.form.get("content", "").strip()
    about_row = query_one("SELECT * FROM about ORDER BY id LIMIT 1")
    if not content:
        flash("About content cannot be empty.", "error")
        return redirect(url_for("dashboard") + "#about-manager")

    db = get_db()
    if about_row:
        db.execute("UPDATE about SET content = ? WHERE id = ?", (content, about_row["id"]))
    else:
        db.execute("INSERT INTO about (content) VALUES (?)", (content,))
    db.commit()
    flash("About section updated successfully.", "success")
    return redirect(url_for("dashboard") + "#about-manager")


@app.route("/add-skill", methods=["POST"])
@admin_required
def add_skill():
    name = request.form.get("name", "").strip()
    level = request.form.get("level", "").strip()
    if not name or not level.isdigit():
        flash("Please provide a skill name and numeric level.", "error")
        return redirect(url_for("dashboard") + "#skills-manager")

    get_db().execute("INSERT INTO skills (name, level) VALUES (?, ?)", (name, max(1, min(100, int(level)))))
    get_db().commit()
    flash("Skill added successfully.", "success")
    return redirect(url_for("dashboard") + "#skills-manager")


@app.route("/edit-skill/<int:skill_id>", methods=["POST"])
@admin_required
def edit_skill(skill_id: int):
    name = request.form.get("name", "").strip()
    level = request.form.get("level", "").strip()
    if not name or not level.isdigit():
        flash("Please provide a valid skill update.", "error")
        return redirect(url_for("dashboard") + "#skills-manager")

    get_db().execute(
        "UPDATE skills SET name = ?, level = ? WHERE id = ?",
        (name, max(1, min(100, int(level))), skill_id),
    )
    get_db().commit()
    flash("Skill updated successfully.", "success")
    return redirect(url_for("dashboard") + "#skills-manager")


@app.route("/delete-skill/<int:skill_id>", methods=["POST"])
@admin_required
def delete_skill(skill_id: int):
    get_db().execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    get_db().commit()
    flash("Skill deleted successfully.", "success")
    return redirect(url_for("dashboard") + "#skills-manager")


@app.route("/add-service", methods=["POST"])
@admin_required
def add_service():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title or not description:
        flash("Service title and description are required.", "error")
        return redirect(url_for("dashboard") + "#services-manager")

    get_db().execute("INSERT INTO services (title, description) VALUES (?, ?)", (title, description))
    get_db().commit()
    flash("Service added successfully.", "success")
    return redirect(url_for("dashboard") + "#services-manager")


@app.route("/edit-service/<int:service_id>", methods=["POST"])
@admin_required
def edit_service(service_id: int):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title or not description:
        flash("Service title and description are required.", "error")
        return redirect(url_for("dashboard") + "#services-manager")

    get_db().execute("UPDATE services SET title = ?, description = ? WHERE id = ?", (title, description, service_id))
    get_db().commit()
    flash("Service updated successfully.", "success")
    return redirect(url_for("dashboard") + "#services-manager")


@app.route("/delete-service/<int:service_id>", methods=["POST"])
@admin_required
def delete_service(service_id: int):
    get_db().execute("DELETE FROM services WHERE id = ?", (service_id,))
    get_db().commit()
    flash("Service deleted successfully.", "success")
    return redirect(url_for("dashboard") + "#services-manager")


@app.route("/add-tool", methods=["POST"])
@admin_required
def add_tool():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Tool name cannot be empty.", "error")
        return redirect(url_for("dashboard") + "#tools-manager")

    get_db().execute("INSERT INTO tools (name) VALUES (?)", (name,))
    get_db().commit()
    flash("Tool added successfully.", "success")
    return redirect(url_for("dashboard") + "#tools-manager")


@app.route("/edit-tool/<int:tool_id>", methods=["POST"])
@admin_required
def edit_tool(tool_id: int):
    name = request.form.get("name", "").strip()
    if not name:
        flash("Tool name cannot be empty.", "error")
        return redirect(url_for("dashboard") + "#tools-manager")

    get_db().execute("UPDATE tools SET name = ? WHERE id = ?", (name, tool_id))
    get_db().commit()
    flash("Tool updated successfully.", "success")
    return redirect(url_for("dashboard") + "#tools-manager")


@app.route("/delete-tool/<int:tool_id>", methods=["POST"])
@admin_required
def delete_tool(tool_id: int):
    get_db().execute("DELETE FROM tools WHERE id = ?", (tool_id,))
    get_db().commit()
    flash("Tool deleted successfully.", "success")
    return redirect(url_for("dashboard") + "#tools-manager")


@app.route("/add-learning", methods=["POST"])
@admin_required
def add_learning():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Learning topic cannot be empty.", "error")
        return redirect(url_for("dashboard") + "#learning-manager")

    get_db().execute("INSERT INTO learning (title) VALUES (?)", (title,))
    get_db().commit()
    flash("Learning topic added successfully.", "success")
    return redirect(url_for("dashboard") + "#learning-manager")


@app.route("/edit-learning/<int:item_id>", methods=["POST"])
@admin_required
def edit_learning(item_id: int):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Learning topic cannot be empty.", "error")
        return redirect(url_for("dashboard") + "#learning-manager")

    get_db().execute("UPDATE learning SET title = ? WHERE id = ?", (title, item_id))
    get_db().commit()
    flash("Learning topic updated successfully.", "success")
    return redirect(url_for("dashboard") + "#learning-manager")


@app.route("/delete-learning/<int:item_id>", methods=["POST"])
@admin_required
def delete_learning(item_id: int):
    get_db().execute("DELETE FROM learning WHERE id = ?", (item_id,))
    get_db().commit()
    flash("Learning topic deleted successfully.", "success")
    return redirect(url_for("dashboard") + "#learning-manager")


@app.route("/add-project", methods=["GET", "POST"])
@admin_required
def add_project():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        tech_stack = request.form.get("tech_stack", "").strip()
        problem_statement = request.form.get("problem_statement", "").strip()
        approach = request.form.get("approach", "").strip()
        impact = request.form.get("impact", "").strip()
        github_link = request.form.get("github_link", "").strip()
        uploaded_image = request.files.get("image")
        image_path = save_uploaded_project_image(uploaded_image)

        if not all([title, description, tech_stack, problem_statement, approach, impact]):
            flash("Please fill in all project fields.", "error")
            return render_template("add_project.html", project=None)

        if uploaded_image and uploaded_image.filename and not image_path:
            flash("Unsupported project image format.", "error")
            return render_template("add_project.html", project=None)

        get_db().execute(
            """
            INSERT INTO projects (title, description, tech_stack, image, github_link, problem_statement, approach, impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, description, tech_stack, image_path, github_link, problem_statement, approach, impact),
        )
        get_db().commit()
        flash("Project added successfully.", "success")
        return redirect(url_for("dashboard") + "#projects-manager")

    return render_template("add_project.html", project=None)


@app.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
@admin_required
def edit_project(project_id: int):
    project = query_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        tech_stack = request.form.get("tech_stack", "").strip()
        problem_statement = request.form.get("problem_statement", "").strip()
        approach = request.form.get("approach", "").strip()
        impact = request.form.get("impact", "").strip()
        github_link = request.form.get("github_link", "").strip()

        if not all([title, description, tech_stack, problem_statement, approach, impact]):
            flash("Please fill in all project fields.", "error")
            return render_template("edit_project.html", project=project)

        image_path = project["image"]
        uploaded_image = request.files.get("image")
        if uploaded_image and uploaded_image.filename:
            saved_path = save_uploaded_project_image(uploaded_image)
            if not saved_path:
                flash("Unsupported project image format.", "error")
                return render_template("edit_project.html", project=project)
            image_path = saved_path

        get_db().execute(
            """
            UPDATE projects
            SET title = ?, description = ?, tech_stack = ?, image = ?, github_link = ?, problem_statement = ?, approach = ?, impact = ?
            WHERE id = ?
            """,
            (title, description, tech_stack, image_path, github_link, problem_statement, approach, impact, project_id),
        )
        get_db().commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("dashboard") + "#projects-manager")

    return render_template("edit_project.html", project=project)


@app.route("/delete-project/<int:project_id>", methods=["POST"])
@admin_required
def delete_project(project_id: int):
    get_db().execute("DELETE FROM projects WHERE id = ?", (project_id,))
    get_db().commit()
    flash("Project deleted successfully.", "success")
    return redirect(url_for("dashboard") + "#projects-manager")


def save_certificate_image(uploaded_file) -> str | None:
    if not uploaded_file or not uploaded_file.filename:
        return None
    if not allowed_image(uploaded_file.filename):
        return None

    safe_name = secure_filename(uploaded_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{safe_name}"
    destination = CERT_IMAGE_DIR / filename
    uploaded_file.save(destination)
    return f"images/certificates/{filename}"


def save_achievement_image(uploaded_file) -> str | None:
    if not uploaded_file or not uploaded_file.filename:
        return None
    if not allowed_image(uploaded_file.filename):
        return None

    safe_name = secure_filename(uploaded_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{safe_name}"
    destination = ACHIEVEMENT_IMAGE_DIR / filename
    uploaded_file.save(destination)
    return f"images/achievements/{filename}"


@app.route("/experiences")
@admin_required
def experiences_manager():
    # Simple server-side search, sort, pagination
    q = request.args.get("q", "").strip()
    page = max(1, int(request.args.get("page", "1")))
    per_page = 10
    sort = request.args.get("sort", "display_order desc, id desc")

    base_query = "SELECT * FROM experience"
    params: list = []
    if q:
        base_query += " WHERE job_title LIKE ? OR company_name LIKE ? OR location LIKE ?"
        qterm = f"%{q}%"
        params.extend([qterm, qterm, qterm])

    # simple ordering sanitization
    if sort not in ("display_order desc, id desc", "created_at desc", "start_date desc", "company_name asc"):
        sort = "display_order desc, id desc"

    rows = query_all(f"{base_query} ORDER BY {sort} LIMIT ? OFFSET ?", tuple(params + [per_page, (page - 1) * per_page]))
    total = query_one(f"SELECT COUNT(*) as c FROM ({base_query})", tuple(params))["c"]

    return render_template("experiences.html", experiences=rows, q=q, page=page, per_page=per_page, total=total, sort=sort)


@app.route("/add-experience", methods=["GET", "POST"])
@admin_required
def add_experience():
    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        company_name = request.form.get("company_name", "").strip()
        employment_type = request.form.get("employment_type", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        current_job = 1 if request.form.get("current_job") == "on" else 0
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        responsibilities = request.form.get("responsibilities", "").strip()
        technologies = request.form.get("technologies", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0

        if not job_title or not company_name:
            flash("Job title and company name are required.", "error")
            return render_template("add_experience.html")

        get_db().execute(
            """
            INSERT INTO experience (job_title, company_name, employment_type, start_date, end_date, current_job, location, description, responsibilities, technologies, display_order, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                job_title,
                company_name,
                employment_type,
                start_date,
                end_date,
                current_job,
                location,
                description,
                responsibilities,
                technologies,
                display_order,
                status,
            ),
        )
        get_db().commit()
        flash("Experience added successfully.", "success")
        return redirect(url_for("experiences_manager"))

    return render_template("add_experience.html")


@app.route("/edit-experience/<int:exp_id>", methods=["GET", "POST"])
@admin_required
def edit_experience(exp_id: int):
    exp = query_one("SELECT * FROM experience WHERE id = ?", (exp_id,))
    if not exp:
        flash("Experience not found.", "error")
        return redirect(url_for("experiences_manager"))

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        company_name = request.form.get("company_name", "").strip()
        employment_type = request.form.get("employment_type", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        current_job = 1 if request.form.get("current_job") == "on" else 0
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        responsibilities = request.form.get("responsibilities", "").strip()
        technologies = request.form.get("technologies", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0

        if not job_title or not company_name:
            flash("Job title and company name are required.", "error")
            return render_template("edit_experience.html", exp=exp)

        get_db().execute(
            """
            UPDATE experience
            SET job_title = ?, company_name = ?, employment_type = ?, start_date = ?, end_date = ?, current_job = ?, location = ?, description = ?, responsibilities = ?, technologies = ?, display_order = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                job_title,
                company_name,
                employment_type,
                start_date,
                end_date,
                current_job,
                location,
                description,
                responsibilities,
                technologies,
                display_order,
                status,
                exp_id,
            ),
        )
        get_db().commit()
        flash("Experience updated successfully.", "success")
        return redirect(url_for("experiences_manager"))

    return render_template("edit_experience.html", exp=exp)


@app.route("/delete-experience/<int:exp_id>", methods=["POST"])
@admin_required
def delete_experience(exp_id: int):
    get_db().execute("DELETE FROM experience WHERE id = ?", (exp_id,))
    get_db().commit()
    flash("Experience deleted successfully.", "success")
    return redirect(url_for("experiences_manager"))


@app.route("/experience/toggle-status/<int:exp_id>", methods=["POST"])
@admin_required
def toggle_experience_status(exp_id: int):
    row = query_one("SELECT status FROM experience WHERE id = ?", (exp_id,))
    if not row:
        return ("", 404)
    new_status = 0 if row["status"] == 1 else 1
    get_db().execute("UPDATE experience SET status = ?, updated_at = datetime('now') WHERE id = ?", (new_status, exp_id))
    get_db().commit()
    return ("", 204)


@app.route("/experience/bulk-action", methods=["POST"])
@admin_required
def experience_bulk_action():
    action = request.form.get("action")
    ids = request.form.getlist("ids")
    if not ids:
        flash("No items selected.", "error")
        return redirect(url_for("experiences_manager"))

    placeholders = ",".join(["?" for _ in ids])
    if action == "delete":
        get_db().execute(f"DELETE FROM experience WHERE id IN ({placeholders})", tuple(ids))
        flash("Selected experiences deleted.", "success")
    elif action in ("activate", "deactivate"):
        status = 1 if action == "activate" else 0
        get_db().execute(f"UPDATE experience SET status = ?, updated_at = datetime('now') WHERE id IN ({placeholders})", tuple([status] + ids))
        flash("Status updated for selected experiences.", "success")

    get_db().commit()
    return redirect(url_for("experiences_manager"))


@app.route("/certifications/bulk-action", methods=["POST"])
@admin_required
def certifications_bulk_action():
    action = request.form.get("action")
    ids = request.form.getlist("ids")
    if not ids:
        flash("No items selected.", "error")
        return redirect(url_for("certifications_manager"))

    placeholders = ",".join(["?" for _ in ids])
    if action == "delete":
        get_db().execute(f"DELETE FROM certifications WHERE id IN ({placeholders})", tuple(ids))
        flash("Selected certifications deleted.", "success")
    elif action in ("activate", "deactivate"):
        status = 1 if action == "activate" else 0
        get_db().execute(f"UPDATE certifications SET status = ?, updated_at = datetime('now') WHERE id IN ({placeholders})", tuple([status] + ids))
        flash("Status updated for selected certifications.", "success")

    get_db().commit()
    return redirect(url_for("certifications_manager"))


@app.route("/achievements/bulk-action", methods=["POST"])
@admin_required
def achievements_bulk_action():
    action = request.form.get("action")
    ids = request.form.getlist("ids")
    if not ids:
        flash("No items selected.", "error")
        return redirect(url_for("achievements_manager"))

    placeholders = ",".join(["?" for _ in ids])
    if action == "delete":
        get_db().execute(f"DELETE FROM achievements WHERE id IN ({placeholders})", tuple(ids))
        flash("Selected achievements deleted.", "success")
    elif action in ("activate", "deactivate"):
        status = 1 if action == "activate" else 0
        get_db().execute(f"UPDATE achievements SET status = ?, updated_at = datetime('now') WHERE id IN ({placeholders})", tuple([status] + ids))
        flash("Status updated for selected achievements.", "success")

    get_db().commit()
    return redirect(url_for("achievements_manager"))


@app.route("/certifications")
@admin_required
def certifications_manager():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")
    page = max(1, int(request.args.get("page", "1")))
    per_page = 10

    base_query = "SELECT * FROM certifications"
    params: list = []
    conditions: list[str] = []
    if q:
        conditions.append("(title LIKE ? OR issuer LIKE ? OR category LIKE ?)")
        qterm = f"%{q}%"
        params.extend([qterm, qterm, qterm])

    if status_filter in ("active", "inactive"):
        conditions.append("status = ?")
        params.append(1 if status_filter == "active" else 0)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    rows = query_all(
        f"{base_query} ORDER BY display_order DESC, created_at DESC LIMIT ? OFFSET ?",
        tuple(params + [per_page, (page - 1) * per_page]),
    )
    total = query_one(f"SELECT COUNT(*) as c FROM ({base_query})", tuple(params))["c"]
    return render_template(
        "certifications.html",
        certs=rows,
        q=q,
        status_filter=status_filter,
        page=page,
        per_page=per_page,
        total=total,
    )


@app.route("/add-certification", methods=["GET", "POST"])
@admin_required
def add_certification():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        issuer = request.form.get("issuer", "").strip()
        issue_date = request.form.get("issue_date", "").strip()
        credential_id = request.form.get("credential_id", "").strip()
        verification_url = request.form.get("verification_url", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0
        image_path = save_certificate_image(request.files.get("image"))

        if not title:
            flash("Certificate title is required.", "error")
            return render_template("add_certificate.html")

        get_db().execute(
            """
            INSERT INTO certifications (title, issuer, issue_date, credential_id, verification_url, image, category, description, display_order, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (title, issuer, issue_date, credential_id, verification_url, image_path, category, description, display_order, status),
        )
        get_db().commit()
        flash("Certification added successfully.", "success")
        return redirect(url_for("certifications_manager"))

    return render_template("add_certificate.html")


@app.route("/edit-certification/<int:cert_id>", methods=["GET", "POST"])
@admin_required
def edit_certification(cert_id: int):
    cert = query_one("SELECT * FROM certifications WHERE id = ?", (cert_id,))
    if not cert:
        flash("Certificate not found.", "error")
        return redirect(url_for("certifications_manager"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        issuer = request.form.get("issuer", "").strip()
        issue_date = request.form.get("issue_date", "").strip()
        credential_id = request.form.get("credential_id", "").strip()
        verification_url = request.form.get("verification_url", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0
        image_path = cert["image"]
        uploaded = request.files.get("image")
        if uploaded and uploaded.filename:
            saved = save_certificate_image(uploaded)
            if saved:
                image_path = saved

        if not title:
            flash("Certificate title is required.", "error")
            return render_template("edit_certificate.html", cert=cert)

        get_db().execute(
            """
            UPDATE certifications
            SET title = ?, issuer = ?, issue_date = ?, credential_id = ?, verification_url = ?, image = ?, category = ?, description = ?, display_order = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (title, issuer, issue_date, credential_id, verification_url, image_path, category, description, display_order, status, cert_id),
        )
        get_db().commit()
        flash("Certification updated successfully.", "success")
        return redirect(url_for("certifications_manager"))

    return render_template("edit_certificate.html", cert=cert)


@app.route("/delete-certification/<int:cert_id>", methods=["POST"])
@admin_required
def delete_certification(cert_id: int):
    get_db().execute("DELETE FROM certifications WHERE id = ?", (cert_id,))
    get_db().commit()
    flash("Certificate deleted successfully.", "success")
    return redirect(url_for("certifications_manager"))


@app.route("/achievements")
@admin_required
def achievements_manager():
    q = request.args.get("q", "").strip()
    page = max(1, int(request.args.get("page", "1")))
    per_page = 10

    base_query = "SELECT * FROM achievements"
    params: list = []
    if q:
        base_query += " WHERE title LIKE ? OR organization LIKE ?"
        qterm = f"%{q}%"
        params.extend([qterm, qterm])

    rows = query_all(f"{base_query} ORDER BY display_order DESC, created_at DESC LIMIT ? OFFSET ?", tuple(params + [per_page, (page - 1) * per_page]))
    total = query_one(f"SELECT COUNT(*) as c FROM ({base_query})", tuple(params))["c"]
    return render_template("achievements.html", achs=rows, q=q, page=page, per_page=per_page, total=total)


@app.route("/add-achievement", methods=["GET", "POST"])
@admin_required
def add_achievement():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        organization = request.form.get("organization", "").strip()
        achievement_date = request.form.get("achievement_date", "").strip()
        description = request.form.get("description", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0
        image_path = save_achievement_image(request.files.get("image"))

        if not title:
            flash("Achievement title is required.", "error")
            return render_template("add_achievement.html")

        get_db().execute(
            """
            INSERT INTO achievements (title, organization, achievement_date, description, image, display_order, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (title, organization, achievement_date, description, image_path, display_order, status),
        )
        get_db().commit()
        flash("Achievement added successfully.", "success")
        return redirect(url_for("achievements_manager"))

    return render_template("add_achievement.html")


@app.route("/edit-achievement/<int:ach_id>", methods=["GET", "POST"])
@admin_required
def edit_achievement(ach_id: int):
    ach = query_one("SELECT * FROM achievements WHERE id = ?", (ach_id,))
    if not ach:
        flash("Achievement not found.", "error")
        return redirect(url_for("achievements_manager"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        organization = request.form.get("organization", "").strip()
        achievement_date = request.form.get("achievement_date", "").strip()
        description = request.form.get("description", "").strip()
        display_order = int(request.form.get("display_order", "0"))
        status = 1 if request.form.get("status") == "on" else 0
        image_path = ach["image"]
        uploaded = request.files.get("image")
        if uploaded and uploaded.filename:
            saved = save_achievement_image(uploaded)
            if saved:
                image_path = saved

        if not title:
            flash("Achievement title is required.", "error")
            return render_template("edit_achievement.html", ach=ach)

        get_db().execute(
            """
            UPDATE achievements
            SET title = ?, organization = ?, achievement_date = ?, description = ?, image = ?, display_order = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (title, organization, achievement_date, description, image_path, display_order, status, ach_id),
        )
        get_db().commit()
        flash("Achievement updated successfully.", "success")
        return redirect(url_for("achievements_manager"))

    return render_template("edit_achievement.html", ach=ach)


@app.route("/delete-achievement/<int:ach_id>", methods=["POST"])
@admin_required
def delete_achievement(ach_id: int):
    get_db().execute("DELETE FROM achievements WHERE id = ?", (ach_id,))
    get_db().commit()
    flash("Achievement deleted successfully.", "success")
    return redirect(url_for("achievements_manager"))


@app.post("/contact")
def contact():
    ensure_contacts_file()

    form_data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "subject": request.form.get("subject", "").strip(),
        "message": request.form.get("message", "").strip(),
    }
    if not all(form_data.values()):
        flash("Please fill in all contact form fields.", "error")
        return redirect(url_for("home") + "#contact")

    with CONTACTS_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                datetime.now().isoformat(timespec="seconds"),
                form_data["name"],
                form_data["email"],
                form_data["subject"],
                form_data["message"],
            ]
        )

    flash("Thanks for reaching out. Your message has been saved successfully.", "success")
    return redirect(url_for("home") + "#contact")


with app.app_context():
    ensure_contacts_file()
    init_database()


if __name__ == "__main__":
    app.run(debug=True)
