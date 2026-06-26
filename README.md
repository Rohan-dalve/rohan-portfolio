# Rohan Dalve Portfolio

A premium Flask portfolio with a recruiter-focused homepage, SQLite-backed content, and a complete admin panel for managing portfolio sections without editing code.

## Project Structure

- `app.py` - Flask app, SQLite setup, authentication, and CRUD routes
- `database.db` - portfolio database created automatically
- `templates/` - public and admin templates
- `static/css/style.css` - premium public and admin styling
- `static/js/main.js` - typing effect, reveals, delete confirmation, and case-study toggles
- `static/images/profile.jpg` - hero profile image
- `static/images/projects/` - uploaded project screenshots
- `static/resume.pdf` - downloadable resume
- `data/contacts.csv` - saved contact form entries
- `requirements.txt` - Python dependencies

## Run Locally

```powershell
cd d:\Portfolio
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`

## Admin Login

Admin route: `http://127.0.0.1:5000/admin`

Default credentials:

- Username: `admin`
- Password: `change-me-now`

Recommended secure setup before running:

```powershell
$env:ADMIN_USERNAME="rohan"
$env:ADMIN_PASSWORD="your-strong-password"
$env:SECRET_KEY="your-secret-key"
python app.py
```

## What You Can Edit From Dashboard

- Main portfolio details: name, role, tagline, email, phone, GitHub, LinkedIn, resume highlights
- About section
- Skills and percentages
- What I Do cards
- Tools I Use section
- Currently Learning section
- Projects in case-study format
- Project screenshots
- Hero profile image

## Project Management

Projects now support:

- short description
- problem statement
- approach / solution
- key results / impact
- tools used
- GitHub link
- project image

## Deploy On Render

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Connect the repository.
4. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. Add environment variables:
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`

## Notes

- Portfolio content is loaded from SQLite, not from hardcoded templates.
- Your profile image should remain at `static/images/profile.jpg`.
- Contact form messages are still stored in `data/contacts.csv`.
