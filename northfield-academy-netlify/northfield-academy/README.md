# Northfield Academy website — Netlify-ready

```
northfield-academy/
├── netlify.toml        Netlify config: build command, publish folder, security + cache headers
├── README.md
├── src/                Source you edit
│   ├── build.py        Generates every page (Python 3.8+, no dependencies)
│   ├── courses.json    All course content
│   └── assets/         CSS + JS
└── site/               Built website — this is what Netlify publishes
    ├── index.html
    ├── courses.html
    ├── courses/        One page per course (6)
    ├── thanks.html     Shown after an enquiry if JavaScript is off
    ├── 404.html        Netlify serves this for missing pages
    ├── privacy.html, refunds.html
    ├── sitemap.xml, robots.txt
    └── assets/
```

## Deploy: option A — drag and drop (2 minutes)

1. Go to https://app.netlify.com/drop and log in.
2. Drag the **`site`** folder (not the whole project) onto the page.
3. Netlify gives you a live URL like `random-name.netlify.app`.
4. In **Site configuration → Forms**, click **Enable form detection**, then drag `site` in again
   (Deploys → drag a new deploy) so Netlify picks up the two enquiry forms.

To update later, rebuild (`python3 src/build.py`) and drag `site` onto the site's **Deploys** tab.

## Deploy: option B — from GitHub (recommended, auto-deploys on every push)

1. Push this whole folder to a GitHub repository.
2. In Netlify: **Add new site → Import an existing project → GitHub**, pick the repo.
3. Netlify reads `netlify.toml`, so the settings fill in by themselves:
   build command `python3 src/build.py`, publish directory `site`. Click **Deploy**.
4. Enable form detection (**Site configuration → Forms**) and trigger one more deploy.

From then on, edit `src/courses.json` or `src/build.py`, commit, push — Netlify rebuilds and publishes.

## Enquiries (Netlify Forms)

Both forms are wired to Netlify Forms — no backend or API keys:
- `demo-enquiry` (home page): name, phone, email, course, timing
- `course-enquiry` (each course page): name, phone, email, course, batch

Each submission also records which page it came from. Submissions appear under **Forms** in the
Netlify dashboard. To get them by email: **Site configuration → Notifications → Emails and webhooks →
Form submission notifications → Add notification → Email**. A hidden honeypot field filters basic spam;
you can add reCAPTCHA later if needed. The free plan includes 100 submissions a month.

When you open the HTML files locally, forms just show the confirmation (nothing is sent).

## Custom domain

**Domain management → Add a domain**, then follow Netlify's DNS steps. HTTPS is issued automatically.
After that, set `"url"` in the `SITE` block at the top of `src/build.py` to your domain and rebuild,
so canonical links, Open Graph tags and `sitemap.xml` point to it.

## Before launch

- Replace everything in [square brackets]: fees, phone, WhatsApp number, address, email,
  instructor names, student quotes. Contact details live in `SITE` in `src/build.py`;
  course details in `src/courses.json`.
- Swap the striped photo placeholders for real images (put files in `src/assets/img/`).
- Write the privacy and refund policies (`build_policy` in `build.py`).
- To embed Google Maps in the contact section, paste the embed `<iframe>` in place of the map
  placeholder; `netlify.toml` already allows `www.google.com` frames.

## Responsive and quality checks done

No horizontal scrolling at 320–1920px; mobile menu, filters, syllabus, tables-as-cards on phones,
form validation and Netlify-style form posts tested in Chromium. Security headers (CSP, frame,
referrer and permissions policies) are set in `netlify.toml`.
