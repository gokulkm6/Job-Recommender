from pathlib import Path
import os
import shutil
from typing import List
import html

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

from mcp_tools.resume_parser import parse_resume as core_parse_resume
from mcp_tools.job_recommender import recommend_jobs as core_recommend_jobs

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Job Recommender")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>Job Recommender</title>
        <style>
          :root {
            --bg: #0b1120;
            --bg-card: #020617;
            --bg-soft: #111827;
            --primary: #6366f1;
            --primary-soft: rgba(99, 102, 241, 0.18);
            --accent: #22c55e;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-subtle: #1f2937;
            --danger: #ef4444;
            --radius-lg: 18px;
            --radius-pill: 999px;
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
                         sans-serif;
            background: radial-gradient(circle at top, #111827, #020617 55%, #000 100%);
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
          }

          .shell {
            width: 100%;
            max-width: 920px;
          }

          .card {
            background: radial-gradient(circle at top left, #111827, #020617);
            border-radius: 28px;
            padding: 28px 32px 26px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow:
              0 24px 80px rgba(15, 23, 42, 0.9),
              0 0 0 1px rgba(15, 23, 42, 0.85);
          }

          .heading-row {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: center;
            margin-bottom: 20px;
          }

          .title-block h1 {
            font-size: 1.6rem;
            margin: 0 0 4px;
            letter-spacing: 0.02em;
          }

          .title-block p {
            margin: 0;
            font-size: 0.9rem;
            color: var(--text-muted);
          }

          .chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 11px;
            border-radius: var(--radius-pill);
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.35);
            font-size: 0.78rem;
            color: var(--text-muted);
            white-space: nowrap;
          }

          .chip-dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.25);
          }

          .upload-zone {
            margin-top: 18px;
            padding: 18px 18px 16px;
            border-radius: 20px;
            border: 1px dashed rgba(148, 163, 184, 0.5);
            background: linear-gradient(
              120deg,
              rgba(15, 23, 42, 0.9),
              rgba(15, 23, 42, 0.96)
            );
          }

          .upload-row {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
            justify-content: space-between;
          }

          .upload-info {
            flex: 1 1 220px;
          }

          .upload-info h2 {
            margin: 0 0 6px;
            font-size: 1rem;
          }

          .upload-info p {
            margin: 0;
            font-size: 0.8rem;
            color: var(--text-muted);
          }

          .upload-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: flex-end;
            align-items: center;
          }

          .file-input-wrapper {
            position: relative;
            overflow: hidden;
            border-radius: var(--radius-pill);
            border: 1px solid rgba(148, 163, 184, 0.4);
            padding: 6px 10px;
            font-size: 0.82rem;
            background: rgba(15, 23, 42, 0.9);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
          }

          .file-input-wrapper span.label-text {
            opacity: 0.9;
          }

          .file-input-wrapper input[type="file"] {
            position: absolute;
            inset: 0;
            opacity: 0;
            cursor: pointer;
          }

          .file-name {
            font-size: 0.78rem;
            color: var(--text-muted);
            max-width: 220px;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
          }

          .btn-primary {
            border: none;
            border-radius: var(--radius-pill);
            padding: 9px 18px;
            font-size: 0.86rem;
            font-weight: 500;
            letter-spacing: 0.02em;
            background: linear-gradient(135deg, #6366f1, #22c55e);
            color: #0b1120;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.45);
            display: inline-flex;
            align-items: center;
            gap: 6px;
          }

          .btn-primary:hover {
            filter: brightness(1.04);
          }

          .btn-primary:active {
            transform: translateY(1px);
            box-shadow: 0 5px 16px rgba(79, 70, 229, 0.6);
          }

          .btn-primary span.dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: #0b1120;
          }

          .helper-row {
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            font-size: 0.78rem;
            color: var(--text-muted);
            opacity: 0.9;
          }

          .helper-row span {
            display: inline-flex;
            align-items: center;
            gap: 6px;
          }

          .helper-row .pill-soft {
            padding: 3px 9px;
            border-radius: var(--radius-pill);
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.3);
            font-size: 0.74rem;
          }

          @media (max-width: 640px) {
            .card {
              padding: 20px 18px 18px;
            }
            .heading-row {
              flex-direction: column;
              align-items: flex-start;
            }
            .upload-row {
              flex-direction: column;
              align-items: flex-start;
            }
            .upload-controls {
              justify-content: flex-start;
            }
          }
        </style>
      </head>
      <body>
        <div class="shell">
          <div class="card">
            <div class="heading-row">
              <div class="title-block">
                <h1>Job Recommender</h1>
                <p>Upload a resume (PDF) and get skill-based job matches.</p>
              </div>
              <div class="chip">
                <span class="chip-dot"></span>
                MCP-ready · FastAPI
              </div>
            </div>

            <form action="/upload_resume/" enctype="multipart/form-data" method="post">
              <div class="upload-zone">
                <div class="upload-row">
                  <div class="upload-info">
                    <h2>Upload your resume</h2>
                    <p>We’ll extract skills and recommend matching roles.</p>
                  </div>
                  <div class="upload-controls">
                    <label class="file-input-wrapper">
                      <span class="label-text">Choose file (PDF)</span>
                      <span id="file-name" class="file-name"></span>
                      <input name="file" type="file" accept=".pdf" required />
                    </label>
                    <button type="submit" class="btn-primary">
                      <span class="dot"></span>
                      <span>Analyze & Recommend</span>
                    </button>
                  </div>
                </div>
                <div class="helper-row">
                  <span>
                    Supported: <span class="pill-soft">PDF</span>
                  </span>
                </div>
              </div>
            </form>
          </div>
        </div>

        <script>
          document.addEventListener("DOMContentLoaded", function () {{
            const fileInput = document.querySelector('input[name="file"]');
            const fileNameSpan = document.getElementById("file-name");

            if (fileInput && fileNameSpan) {{
              fileInput.addEventListener("change", function () {{
                if (fileInput.files && fileInput.files.length > 0) {{
                  fileNameSpan.textContent = fileInput.files[0].name;
                }} else {{
                  fileNameSpan.textContent = "";
                }}
              }});
            }}
          }});
        </script>
      </body>
    </html>
    """

@app.post("/upload_resume/", response_class=HTMLResponse)
async def upload_resume(file: UploadFile = File(...)):
    file_path = UPLOAD_FOLDER / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed = core_parse_resume(str(file_path))
    skills: List[str] = parsed.get("skills", [])
    jobs = core_recommend_jobs(skills, top_k=5)

    emails = parsed.get("emails", [])
    phones = parsed.get("phones", [])
    summary = parsed.get("summary", {}) or {}
    num_chars = summary.get("num_chars", 0)
    num_tokens = summary.get("num_tokens", 0)

    def pills(items, extra_class: str = "") -> str:
        if not items:
            return f"<span class='muted'>None detected</span>"
        return "".join(
            f"<span class='pill {extra_class}'>{html.escape(str(x))}</span>"
            for x in items
        )

    emails_html = pills(emails)
    phones_html = pills(phones)
    skills_html = pills(skills, "pill-soft")

    job_cards = []
    for job in jobs:
        title = html.escape(str(job.get("title", "Untitled role")))
        location = html.escape(str(job.get("location", "N/A")))
        description = html.escape(str(job.get("description", "")))
        job_skills = [str(s) for s in job.get("skills", [])]
        match_score = int(job.get("match_score", 0))
        bar_width = min(100, match_score * 25)

        job_skills_html = (
            "".join(
                f"<span class='pill pill-soft'>{html.escape(s)}</span>"
                for s in job_skills
            )
            if job_skills
            else "<span class='muted'>No specific skills listed</span>"
        )

        job_cards.append(
            f"""
            <div class="job-card">
              <div class="job-header">
                <div>
                  <h3>{title}</h3>
                  <p class="job-location">{location}</p>
                </div>
                <div class="match-score">
                  <span>Match score: {match_score}</span>
                  <div class="bar-outer">
                    <div class="bar-inner" style="width: {bar_width}%;"></div>
                  </div>
                </div>
              </div>
              <p class="job-description">{description}</p>
              <div class="job-skills">
                {job_skills_html}
              </div>
            </div>
            """
        )

    jobs_html = "".join(job_cards) if job_cards else "<p class='muted'>No jobs matched.</p>"

    return f"""
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>Results · Job Recommender</title>
        <style>
          :root {{
            --bg: #020617;
            --bg-card: #020617;
            --bg-soft: #020617;
            --primary: #6366f1;
            --accent: #22c55e;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border-subtle: #1f2937;
            --radius-lg: 18px;
            --radius-pill: 999px;
          }}

          * {{
            box-sizing: border-box;
          }}

          body {{
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
                         sans-serif;
            background: radial-gradient(circle at top, #111827, #020617 55%, #000 100%);
            color: var(--text-main);
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 24px;
          }}

          .shell {{
            width: 100%;
            max-width: 1120px;
          }}

          .header-row {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: center;
            margin-bottom: 18px;
          }}

          .header-row h1 {{
            margin: 0;
            font-size: 1.5rem;
          }}

          .header-row p {{
            margin: 4px 0 0;
            font-size: 0.86rem;
            color: var(--text-muted);
          }}

          .back-link {{
            font-size: 0.82rem;
            text-decoration: none;
            color: var(--text-muted);
            padding: 6px 11px;
            border-radius: var(--radius-pill);
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: rgba(15, 23, 42, 0.9);
          }}

          .back-link:hover {{
            color: var(--text-main);
            border-color: rgba(148, 163, 184, 0.8);
          }}

          .layout {{
            display: grid;
            grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
            gap: 18px;
          }}

          .panel {{
            background: radial-gradient(circle at top left, #111827, #020617);
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 18px 18px 16px;
            box-shadow:
              0 20px 70px rgba(15, 23, 42, 0.9),
              0 0 0 1px rgba(15, 23, 42, 0.85);
          }}

          .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
          }}

          .panel-header h2 {{
            margin: 0;
            font-size: 1rem;
          }}

          .panel-header span {{
            font-size: 0.76rem;
            color: var(--text-muted);
          }}

          .grid-two {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 4px;
          }}

          .field {{
            padding: 9px 10px;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.96);
            border: 1px solid rgba(148, 163, 184, 0.2);
          }}

          .field-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 3px;
            display: block;
          }}

          .field-value {{
            font-size: 0.85rem;
          }}

          .pill {{
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: var(--radius-pill);
            background: rgba(15, 23, 42, 0.98);
            border: 1px solid rgba(148, 163, 184, 0.45);
            font-size: 0.78rem;
            margin: 2px 4px 2px 0;
            white-space: nowrap;
          }}

          .pill-soft {{
            border-color: rgba(79, 70, 229, 0.6);
            background: rgba(15, 23, 42, 0.95);
          }}

          .muted {{
            font-size: 0.8rem;
            color: var(--text-muted);
          }}

          .metrics-row {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
          }}

          .metric-pill {{
            flex: 1;
            padding: 7px 10px;
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.35);
            background: rgba(15, 23, 42, 0.96);
            font-size: 0.78rem;
            display: flex;
            justify-content: space-between;
          }}

          .metric-label {{
            color: var(--text-muted);
          }}

          .metric-value {{
            font-variant-numeric: tabular-nums;
          }}

          .job-card {{
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            padding: 12px 13px 11px;
            background: rgba(15, 23, 42, 0.96);
            margin-bottom: 10px;
          }}

          .job-header {{
            display: flex;
            justify-content: space-between;
            gap: 8px;
            align-items: flex-start;
            margin-bottom: 6px;
          }}

          .job-header h3 {{
            margin: 0;
            font-size: 0.98rem;
          }}

          .job-location {{
            margin: 2px 0 0;
            font-size: 0.8rem;
            color: var(--text-muted);
          }}

          .match-score {{
            font-size: 0.78rem;
            text-align: right;
          }}

          .bar-outer {{
            width: 120px;
            height: 6px;
            border-radius: 999px;
            background: rgba(30, 64, 175, 0.3);
            overflow: hidden;
            margin-top: 4px;
          }}

          .bar-inner {{
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #6366f1, #22c55e);
          }}

          .job-description {{
            margin: 0 0 6px;
            font-size: 0.82rem;
            color: var(--text-muted);
          }}

          .job-skills {{
            margin-top: 2px;
          }}

          .footer-row {{
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
          }}

          @media (max-width: 860px) {{
            .layout {{
              grid-template-columns: minmax(0, 1fr);
            }}
          }}

          @media (max-width: 640px) {{
            body {{
              padding: 18px 12px;
            }}
            .panel {{
              padding: 16px 14px 14px;
            }}
            .header-row {{
              flex-direction: column;
              align-items: flex-start;
              gap: 8px;
            }}
          }}
        </style>
      </head>
      <body>
        <div class="shell">
          <div class="header-row">
            <div>
              <h1>Resume analysis report</h1>
              <p>Skill-based job recommendations below.</p>
            </div>
            <a class="back-link" href="/">← Upload another resume</a>
          </div>

          <div class="layout">
            <!-- Left: Candidate snapshot -->
            <section class="panel">
              <div class="panel-header">
                <h2>Candidate snapshot</h2>
                <span>Extracted contact & skill profile</span>
              </div>

              <div class="grid-two">
                <div class="field">
                  <span class="field-label">Emails</span>
                  <div class="field-value">{emails_html}</div>
                </div>
                <div class="field">
                  <span class="field-label">Phones</span>
                  <div class="field-value">{phones_html}</div>
                </div>
              </div>

              <div class="field" style="margin-top:10px;">
                <span class="field-label">Skills detected</span>
                <div class="field-value">{skills_html}</div>
              </div>
            </section>

            <!-- Right: Job recommendations -->
            <section class="panel">
              <div class="panel-header">
                <h2>Job recommendations</h2>
                <span>Ranked by skill overlap & match score</span>
              </div>
              {jobs_html}
            </section>
          </div>

          <div class="footer-row">
            <span>Local processing only · spaCy + rule-based skill extraction</span>
            <span>This is a prototype; do not use for automated hiring decisions.</span>
          </div>
        </div>
      </body>
    </html>
    """  