#!/usr/bin/env python3
"""Build the Northfield Academy static site.

    python3 build.py            # writes ../site (or the folder given with --out)

Edit courses.json to change course content, then rebuild. No dependencies.
"""
import argparse, json, shutil
from html import escape as e
from pathlib import Path

HERE = Path(__file__).parent
SITE = {
    "name": "Northfield Academy",
    "url": "https://www.example.com",          # TODO: your domain (used for canonical + Open Graph)
    "phone_display": "[+91 00000 00000]",
    "phone_href": "+910000000000",
    "whatsapp": "910000000000",
    "email": "[hello@youracademy.com]",
    "address_1": "[Building, street]",
    "address_2": "[Area, city, PIN]",
    "hours": "Monday to Saturday, [9 am to 7 pm]",
    # Set to your form backend URL (Formspree, serverless function, CRM webhook) to receive enquiries.
    "form_endpoint": "",
}
COURSES = json.loads((HERE / "courses.json").read_text(encoding="utf-8"))["courses"]
BY_SLUG = {c["slug"]: c for c in COURSES}
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def batch_key(b):
    return (MONTHS[b["month"]], int(b["day"]))


def next_batch(c):
    open_b = [b for b in c["batches"] if b.get("open")] or c["batches"]
    b = min(open_b, key=batch_key)
    return f'{int(b["day"])} {b["month"]} 2026'


# ---------------------------------------------------------------- icons
CHECK = '<svg class="icon-check" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
MARK = '<svg class="brand__mark" viewBox="0 0 36 36" aria-hidden="true"><rect x="1" y="1" width="34" height="34" rx="6" fill="#1F4D3F"/><path d="M9 25V11l9 9 9-9v14" fill="none" stroke="#E8A317" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'
CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 0 1-13.5 7.8L3 21l1.2-4.5A9 9 0 1 1 21 12z"/></svg>'
OK = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/></svg>'


# ---------------------------------------------------------------- layout
def head(title, description, path, root, extra=""):
    canonical = SITE["url"].rstrip("/") + "/" + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta name="theme-color" content="#F6F7F9">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Source+Sans+3:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{root}assets/css/styles.css">
<script src="{root}assets/js/main.js" defer></script>
{extra}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(root, current, cta_href):
    """current: 'home' | 'courses'. Home anchors resolve to index.html#… on other pages."""
    home = "" if current == "home" else f"{root}index.html"
    links = [
        ("Home", f"{root}index.html", current == "home" and False),
        ("Courses", f"{root}courses.html", current == "courses"),
        ("Batches", f"{home}#batches", False),
        ("Campus", f"{home}#campus", False),
        ("Faculty", f"{home}#faculty", False),
        ("FAQ", f"{home}#faq", False),
        ("Contact", f"{home}#contact", False),
    ]
    if current == "home":
        links = links[1:]
    desk = "\n".join(
        f'<a href="{h}"{" aria-current=\"page\"" if cur else ""}>{t}</a>' for t, h, cur in links)
    mob = "\n".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if cur else ""}>{t}</a></li>' for t, h, cur in links)
    return f"""<header class="site-header">
<div class="container site-header__bar">
<a class="brand" href="{root}index.html">{MARK}<span class="brand__name">{SITE["name"]}</span></a>
<nav class="nav" aria-label="Main">
{desk}
</nav>
<a class="btn btn--accent header-cta" href="{cta_href}">Book a free demo class</a>
<button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu">
<svg class="icon-open" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
<svg class="icon-close" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
</button>
</div>
<nav id="mobile-nav" class="mobile-nav container" aria-label="Mobile" hidden>
<ul>
{mob}
</ul>
<a class="btn btn--accent btn--block" href="{cta_href}">Book a free demo class</a>
</nav>
</header>
"""


def footer(root):
    home = f"{root}index.html"
    return f"""<footer class="site-footer">
<div class="container site-footer__top">
<div>
<div class="site-footer__name">{SITE["name"]}</div>
<p>In-person courses in technology, design and business.<br>{SITE["address_1"]}, {SITE["address_2"]}</p>
</div>
<nav aria-label="Footer">
<ul>
<li><a href="{root}courses.html">All courses</a></li>
<li><a href="{home}#campus">Campus</a></li>
<li><a href="{home}#faculty">Faculty</a></li>
<li><a href="{home}#faq">FAQ</a></li>
<li><a href="{home}#contact">Contact</a></li>
</ul>
</nav>
</div>
<div class="container site-footer__bottom">
<span>© <span data-year>2026</span> {SITE["name"]}</span>
<ul><li><a href="{root}privacy.html">Privacy policy</a></li><li><a href="{root}refunds.html">Refund policy</a></li></ul>
</div>
</footer>
</body>
</html>
"""


def page(title, description, path, root, current, body, cta_href="#enquire", extra_head=""):
    return head(title, description, path, root, extra_head) + header(root, current, cta_href) + body + footer(root)


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


# ---------------------------------------------------------------- shared pieces
def batch_item(day, month, title, time, is_open):
    pill = '<span class="pill pill--open">Enrolling</span>' if is_open else '<span class="pill pill--wait">Waitlist</span>'
    return f"""<li class="board__item">
<div class="date-chip"><div class="date-chip__day">{e(day)}</div><div class="date-chip__month">{e(month)}</div></div>
<div><div class="board__course">{title}</div><div class="board__time">{e(time)}</div>{pill}</div>
</li>"""


def form_block(form_id, course_field_html, success_title, success_text, submit_label):
    endpoint = f' data-endpoint="{e(SITE["form_endpoint"])}"' if SITE["form_endpoint"] else ""
    return f"""<div class="form-card" data-enquiry-wrap>
<div class="form-success" data-success hidden tabindex="-1" role="status">
{OK}
<h3>{success_title}</h3>
<p>{success_text}</p>
<button type="button" class="btn btn--outline" data-again>Send another enquiry</button>
</div>
<form class="form" data-enquiry novalidate{endpoint}>
<div class="field"><label for="{form_id}-name">Full name</label><input class="input" id="{form_id}-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="{form_id}-phone">Phone number</label><input class="input" id="{form_id}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
<div class="field"><label for="{form_id}-email">Email <span class="optional">(optional)</span></label><input class="input" id="{form_id}-email" name="email" type="email" autocomplete="email"></div>
{course_field_html}
<p class="form-error" data-error role="alert" hidden></p>
<button type="submit" class="btn btn--primary btn--lg btn--block">{submit_label}</button>
<p class="form-note">We only use your details to contact you about this enquiry.</p>
</form>
</div>"""


# ---------------------------------------------------------------- home
def build_home():
    board_rows = []
    rows = []
    for c in COURSES:
        for b in c["batches"]:
            rows.append((batch_key(b), b, c))
    rows.sort(key=lambda r: r[0])
    for _, b, c in rows[:4]:
        board_rows.append(batch_item(b["day"], b["month"], e(c["title"]), f'{b["days"]}, {b["time"]}', b.get("open")))

    cats = ["All", "Technology", "Design", "Business", "Communication"]
    chips = "\n".join(
        f'<button type="button" class="chip" data-filter="cat" data-value="{c}" aria-pressed="{str(c == "All").lower()}">{c}</button>' for c in cats)
    cards = "\n".join(f"""<article class="course-card" data-item data-cat="{e(c["cat"])}">
<div class="kicker">{e(c["cat"])}</div>
<h3 class="h-card"><a href="courses/{c["slug"]}.html" style="text-decoration:none">{e(c["title"])}</a></h3>
<p class="course-card__desc">{e(c["desc"])}</p>
<dl class="facts-mini">
<div><dt>Duration</dt><dd>{e(c["duration"])}</dd></div>
<div><dt>Level</dt><dd>{e(c["level"])}</dd></div>
<div><dt>Timings</dt><dd>{e(" / ".join(c["timings"]))}</dd></div>
<div><dt>Fee</dt><dd>{e(c["fee"])}</dd></div>
</dl>
<div class="course-card__actions">
<a class="btn btn--primary" href="courses/{c["slug"]}.html">View course<span class="visually-hidden">: {e(c["title"])}</span></a>
<a class="btn btn--outline" href="#enquire" data-enquire-course="{e(c["title"])}">Enquire<span class="visually-hidden"> about {e(c["title"])}</span></a>
</div>
</article>""" for c in COURSES)

    faculty = [
        ("Lead, Web Development", "[Years] years building web products at [company]. Teaches the full-stack course."),
        ("Lead, Data Analytics", "[Years] years as a data analyst in [industry]. Teaches the analytics course."),
        ("Lead, Design", "[Years] years as a product designer at [company]. Teaches the UI/UX course."),
    ]
    fac = "\n".join(f"""<div class="person">
<div class="photo-ph portrait" role="img" aria-label="Photo placeholder: instructor portrait">[Portrait]</div>
<h3>[Instructor name]</h3><div class="person__role">{r}</div><p>{b}</p>
</div>""" for r, b in faculty)

    quote = """<figure class="quote">
<svg width="32" height="24" viewBox="0 0 32 24" aria-hidden="true"><path d="M0 24V14C0 6 4 1 12 0v5c-4 1-6 4-6 8h6v11zm18 0V14c0-8 4-13 12-14v5c-4 1-6 4-6 8h6v11z" fill="#E8A317"/></svg>
<blockquote>[Student quote: two or three sentences about what changed for them after the course.]</blockquote>
<figcaption><strong>[Student name]</strong><br>[Course], now [role] at [company]</figcaption>
</figure>"""

    faqs = [
        ("Do I need any prior experience?", "No. Every course starts from the basics. If you already know some of the material, the counsellor can suggest a batch that moves faster."),
        ("What happens if I miss a class?", "Each session has notes and practice tasks, and you can attend the same topic in a parallel batch or use open lab hours to catch up with a mentor."),
        ("Can I pay the fee in instalments?", "Yes. Most courses can be paid in [2 to 3] instalments. Ask about the plan for your course during counselling."),
        ("Is there placement support?", "After you complete the course and the final project, we help with your resume, run mock interviews and share openings from our hiring partners."),
        ("Do you offer weekend batches?", "Yes. Most courses have weekday, evening and weekend options. The batch board above shows the next start dates."),
    ]
    faq_html = "\n".join(
        f'<details{" open" if i == 0 else ""}><summary>{q}</summary><div class="accordion__body"><p>{a}</p></div></details>'
        for i, (q, a) in enumerate(faqs))
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
    org_ld = jsonld({"@context": "https://schema.org", "@type": "EducationalOrganization", "name": SITE["name"],
                     "url": SITE["url"], "telephone": SITE["phone_href"],
                     "address": {"@type": "PostalAddress", "streetAddress": SITE["address_1"], "addressLocality": SITE["address_2"]}})

    options = "\n".join(f'<option value="{e(c["title"])}">{e(c["title"])}</option>' for c in COURSES)
    course_field = f"""<div class="field"><label for="enq-course">Course you are interested in</label>
<select class="input" id="enq-course" name="course"><option value="">Not sure yet, help me choose</option>
{options}
</select></div>
<fieldset class="field"><legend>Preferred timing</legend><div class="radio-row">
<label class="radio"><input type="radio" name="timing" value="Weekday" checked>Weekday</label>
<label class="radio"><input type="radio" name="timing" value="Weekend">Weekend</label>
<label class="radio"><input type="radio" name="timing" value="Evening">Evening</label>
</div></fieldset>"""
    form = form_block("enq", course_field, "Enquiry sent",
                      'Thanks, <span data-success-name></span>. A counsellor will call you within one working day to book your demo class for <span data-success-course></span>.',
                      "Book my free demo class")

    body = f"""<main id="main">
<section class="hero container">
<div class="split split--center">
<div>
<h1 class="h-display">Learn it in a classroom, with a teacher beside you.</h1>
<p class="lead">Job-ready courses in development, data, design and business, taught in person in small batches. You build real work in our labs and get feedback on it the same day.</p>
<div class="btn-row">
<a class="btn btn--primary btn--lg" href="#enquire">Book a free demo class</a>
<a class="btn btn--outline btn--lg" href="courses.html">Browse courses</a>
</div>
<ul class="hero__points">
<li>{CHECK}Batches capped at [20] students</li>
<li>{CHECK}Weekday, evening and weekend timings</li>
<li>{CHECK}Placement support after you finish</li>
</ul>
</div>
<div id="batches" class="board">
<div class="board__head"><h2 class="board__title">Next batches</h2><span class="board__note">Updated every Monday</span></div>
<ul class="board__list">
{chr(10).join(board_rows)}
</ul>
<a class="btn btn--accent btn--block" href="#enquire">Reserve a seat</a>
</div>
</div>
</section>

<section class="section section--white">
<div class="container">
<h2 class="h-section" style="max-width:18em">Why people choose a classroom over another video course</h2>
<div class="grid-auto" style="margin-top:44px">
<div class="feature"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.4 3.4-5.5 6.5-5.5s5.7 2.1 6.5 5.5"/><circle cx="17.5" cy="9" r="2.5"/><path d="M16.5 14.6c2.5.3 4.3 2.2 5 5.4"/></svg><h3>Small batches</h3><p>No more than [20] students per batch, so your instructor knows your name, your code and where you get stuck.</p></div>
<div class="feature"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/></svg><h3>A seat in a working lab</h3><p>Every student gets a configured machine, fast internet and the licensed software the course needs. Bring a laptop if you prefer.</p></div>
<div class="feature"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h5"/></svg><h3>Projects, not just notes</h3><p>Each course ends with a portfolio project you present to the class and a reviewer, the same way you would at work.</p></div>
<div class="feature"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 7h18v13H3z"/><path d="M8 7V4h8v3"/><path d="M3 12h18"/></svg><h3>Help getting hired</h3><p>Resume reviews, mock interviews and introductions to our hiring partners once you complete the course.</p></div>
</div>
</div>
</section>

<section id="courses" class="section container" data-filter-scope>
<div class="section-head">
<div><h2 class="h-section">Courses</h2><p class="section-intro">All courses run on campus. Fees include lab access, study material and a completion certificate.</p></div>
<div class="chips chips--scroll" role="group" aria-label="Filter courses by subject">
{chips}
</div>
</div>
<p class="visually-hidden" data-filter-status role="status"></p>
<div class="card-grid" data-filter-list>
{cards}
</div>
<div class="center-row"><a class="btn btn--outline btn--lg" href="courses.html">See all courses, compare timings and fees</a></div>
</section>

<section class="section section--navy">
<div class="container">
<h2 class="h-section">How joining works</h2>
<ol class="steps">
<li><div class="steps__num" aria-hidden="true">1</div><h3>Send an enquiry</h3><p>Fill in the form or call us. A counsellor gets back to you within one working day.</p></li>
<li><div class="steps__num" aria-hidden="true">2</div><h3>Sit in a free demo class</h3><p>Join a live session with a current batch and meet the instructor before you pay anything.</p></li>
<li><div class="steps__num" aria-hidden="true">3</div><h3>Pick your course and batch</h3><p>We match you to a course and timing that fits your goals, background and schedule.</p></li>
<li><div class="steps__num" aria-hidden="true">4</div><h3>Enroll and start</h3><p>Pay in full or in instalments, collect your ID card and kit, and start with your batch.</p></li>
</ol>
</div>
</section>

<section id="campus" class="section container">
<div class="split split--center split--even">
<div class="campus-photos">
<div class="photo-ph" role="img" aria-label="Photo placeholder: classroom">[Photo: classroom during a session]</div>
<div class="photo-ph" role="img" aria-label="Photo placeholder: computer lab">[Photo: computer lab]</div>
<div class="photo-ph" role="img" aria-label="Photo placeholder: student lounge">[Photo: student lounge]</div>
</div>
<div>
<h2 class="h-section">Our campus</h2>
<p class="section-intro">A short walk from [nearest metro or bus stop]. Come in any day between [9 am and 7 pm] to look around.</p>
<ul class="checklist">
<li>{CHECK}Air-conditioned classrooms with projectors and whiteboards</li>
<li>{CHECK}Computer lab with [40] machines and power backup</li>
<li>{CHECK}Open practice hours outside class time</li>
<li>{CHECK}Library, discussion rooms and a student lounge</li>
</ul>
</div>
</div>
</section>

<section id="faculty" class="section section--white">
<div class="container">
<h2 class="h-section">Learn from people who do this for a living</h2>
<p class="section-intro">Our instructors work in the fields they teach and spend their days with students, not slides.</p>
<div class="grid-auto" style="margin-top:40px">
{fac}
</div>
</div>
</section>

<section class="section container">
<h2 class="h-section">What our students say</h2>
<div class="grid-auto" style="margin-top:40px;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))">
{quote}
{quote}
{quote}
</div>
</section>

<section id="faq" class="section section--white">
<div class="container" style="max-width:860px">
<h2 class="h-section">Questions people ask before joining</h2>
<div class="accordion">
{faq_html}
</div>
</div>
</section>

<section id="enquire" class="section section--green on-dark">
<div class="container split split--form">
<div>
<h2 class="h-section">Come and sit in on a class</h2>
<p class="lead" style="margin-top:18px">The demo class is free and there is no obligation to join. Tell us what you are interested in and we will call to fix a time.</p>
<div class="contact-links">
<a href="tel:{SITE["phone_href"]}">{PHONE}{SITE["phone_display"]}</a>
<a href="https://wa.me/{SITE["whatsapp"]}">{CHAT}Chat on WhatsApp</a>
</div>
</div>
{form}
</div>
</section>

<section id="contact" class="section container">
<div class="split">
<div>
<h2 class="h-section">Visit us</h2>
<address class="address">
<div><strong>Address</strong><span>{SITE["address_1"]}<br>{SITE["address_2"]}</span></div>
<div><strong>Phone</strong><a href="tel:{SITE["phone_href"]}">{SITE["phone_display"]}</a></div>
<div><strong>Email</strong><a href="mailto:{SITE["email"].strip("[]")}">{SITE["email"]}</a></div>
<div><strong>Office hours</strong><span>{SITE["hours"]}</span></div>
</address>
</div>
<div class="photo-ph map-ph" role="img" aria-label="Map placeholder">[Embedded map]</div>
</div>
</section>
</main>
"""
    return page(f'{SITE["name"]} — In-person courses in tech, design and business',
                "Job-ready courses in web development, data analytics, design, marketing, accounting and spoken English, taught in person in small batches.",
                "", "", "home", body, extra_head=org_ld + faq_ld)


# ---------------------------------------------------------------- courses catalogue
def build_catalogue():
    cats = ["All", "Technology", "Design", "Business", "Communication"]
    times = ["Any", "Weekday", "Evening", "Weekend"]
    cat_chips = "\n".join(f'<button type="button" class="chip" data-filter="cat" data-value="{c}" aria-pressed="{str(c == "All").lower()}">{c}</button>' for c in cats)
    time_chips = "\n".join(f'<button type="button" class="chip chip--green" data-filter="time" data-value="{t}" aria-pressed="{str(t == "Any").lower()}">{t}</button>' for t in times)
    rows = "\n".join(f"""<article class="course-row" data-item data-cat="{e(c["cat"])}" data-timings="{" ".join(c["timings"])}">
<div>
<div class="kicker">{e(c["cat"])}</div>
<h2><a href="courses/{c["slug"]}.html">{e(c["title"])}</a></h2>
<p class="course-row__desc">{e(c["desc"])}</p>
<ul class="tags">{"".join(f"<li>{t} batch</li>" for t in c["timings"])}</ul>
</div>
<div class="course-row__side">
<dl class="facts-mini">
<div><dt>Duration</dt><dd>{e(c["duration"])}</dd></div>
<div><dt>Level</dt><dd>{e(c["level"])}</dd></div>
<div><dt>Next batch</dt><dd>{next_batch(c)}</dd></div>
<div><dt>Fee</dt><dd>{e(c["fee"])}</dd></div>
</dl>
<a class="btn btn--primary btn--block" href="courses/{c["slug"]}.html">View course<span class="visually-hidden">: {e(c["title"])}</span></a>
</div>
</article>""" for c in COURSES)
    table = "\n".join(f"""<tr>
<th scope="row"><a href="courses/{c["slug"]}.html">{e(c["title"])}</a></th>
<td data-label="Duration">{e(c["duration"])}</td>
<td data-label="Class time">{e(c["hours"])}</td>
<td data-label="Timings">{e(", ".join(c["timings"]))}</td>
<td data-label="Next batch">{next_batch(c)}</td>
<td data-label="Fee">{e(c["fee"])}</td>
</tr>""" for c in COURSES)
    ld = jsonld({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f'{SITE["url"]}/courses/{c["slug"]}.html', "name": c["title"]}
        for i, c in enumerate(COURSES)]})

    body = f"""<main id="main">
<section class="container" style="padding-top:20px">
<nav class="breadcrumb" aria-label="Breadcrumb" style="padding-top:0"><ol><li><a href="index.html">Home</a></li><li aria-hidden="true">/</li><li aria-current="page">Courses</li></ol></nav>
<h1 class="h-page" style="margin-top:14px">All courses</h1>
<p class="lead" style="margin-top:18px;max-width:36em">Six career courses, all taught in person on our campus. Filter by subject or by the time of day you can attend, then open a course to see its full syllabus, batches and fees.</p>
</section>

<div class="container" data-filter-scope style="padding-top:32px;padding-bottom:var(--section-y)">
<div class="filter-panel" role="group" aria-label="Filter courses">
<div class="filter-group"><span class="filter-group__label" id="lbl-subject">Subject</span><div class="chips chips--scroll" role="group" aria-labelledby="lbl-subject">{cat_chips}</div></div>
<div class="filter-group"><span class="filter-group__label" id="lbl-time">Timing</span><div class="chips chips--scroll" role="group" aria-labelledby="lbl-time">{time_chips}</div></div>
</div>
<p class="filter-status" data-filter-status role="status">Showing all {len(COURSES)} courses</p>
<div class="course-list" data-filter-list style="margin-top:18px">
{rows}
</div>
<div class="empty-state" data-filter-empty hidden style="margin-top:18px">
<h2>No course matches both filters</h2>
<p>Try a different timing, or clear the filters to see every course. New batch timings are added each month.</p>
<button type="button" class="btn btn--primary" data-filter-reset>Clear filters</button>
</div>
</div>

<section id="compare" class="section section--white">
<div class="container">
<h2 class="h-section">Compare courses</h2>
<div class="table-wrap">
<table class="data-table data-table--wide data-table--stack">
<caption class="visually-hidden">Course comparison: duration, class time, timings, next batch and fee</caption>
<thead><tr><th scope="col">Course</th><th scope="col">Duration</th><th scope="col">Class time</th><th scope="col">Timings</th><th scope="col">Next batch</th><th scope="col">Fee</th></tr></thead>
<tbody>
{table}
</tbody>
</table>
</div>
</div>
</section>

<section class="section section--green on-dark">
<div class="container split split--center">
<div>
<h2 class="h-section">Not sure which course fits you?</h2>
<p class="lead" style="margin-top:14px">Talk to a counsellor for 15 minutes. We will ask about your background and goals and suggest a course and batch, or tell you honestly if none of ours is right.</p>
</div>
<div class="btn-row">
<a class="btn btn--accent btn--lg" href="index.html#enquire">Talk to a counsellor</a>
<a class="btn btn--outline-light btn--lg" href="tel:{SITE["phone_href"]}">Call {SITE["phone_display"]}</a>
</div>
</div>
</section>
</main>
"""
    return page(f'All courses — {SITE["name"]}',
                "Compare every in-person course at Northfield Academy: duration, timings, next batch dates and fees.",
                "courses.html", "", "courses", body, cta_href="index.html#enquire", extra_head=ld)


# ---------------------------------------------------------------- course detail
def build_course(c):
    root = "../"
    batches_sorted = sorted(c["batches"], key=batch_key)
    board = "\n".join(batch_item(b["day"], b["month"], f'{e(b["type"])} batch', f'{b["days"]}, {b["time"]}', b.get("open")) for b in batches_sorted)
    outcomes = "\n".join(f"<li>{CHECK}<span>{e(o)}</span></li>" for o in c["outcomes"])
    for_who = "\n".join(f"<li>{e(w)}</li>" for w in c["forWho"])
    modules = "\n".join(f"""<details{" open" if i == 0 else ""}>
<summary><span class="syllabus__num" aria-hidden="true">{i + 1}</span><span>{e(m["title"])}</span><span class="syllabus__weeks">{e(m["weeks"])}</span></summary>
<div class="accordion__body"><ul>{"".join(f"<li>{e(t)}</li>" for t in m["topics"])}</ul></div>
</details>""" for i, m in enumerate(c["modules"]))
    projects = "\n".join(f'<div><h3>{e(p["title"])}</h3><p>{e(p["desc"])}</p></div>' for p in c["projects"])
    tools = "".join(f"<li>{e(t)}</li>" for t in c["tools"])
    table = "\n".join(f"""<tr>
<th scope="row">{e(b["type"])}</th>
<td data-label="Days">{e(b["days"])}</td>
<td data-label="Time">{e(b["time"])}</td>
<td data-label="Starts">{int(b["day"])} {b["month"]} 2026</td>
<td data-label="Status">{'<span class="pill pill--open-light">Enrolling</span>' if b.get("open") else '<span class="pill pill--wait-light">Waitlist</span>'}</td>
</tr>""" for b in batches_sorted)
    others = [o for o in COURSES if o["slug"] != c["slug"]]
    # Prefer same-category courses first
    others.sort(key=lambda o: (o["cat"] != c["cat"]))
    related = "\n".join(f"""<a class="related" href="{o["slug"]}.html">
<div class="kicker">{e(o["cat"])}</div><div class="related__title">{e(o["title"])}</div><div class="related__meta">{e(o["duration"])}, {e(o["level"])}</div>
</a>""" for o in others[:3])

    radios = "\n".join(
        f'<label class="radio radio--stack"><input type="radio" name="batch" value="{e(b["type"])}"{" checked" if i == 0 else ""}><span><strong>{e(b["type"])}</strong>, {e(b["days"])}, {e(b["time"])}</span></label>'
        for i, b in enumerate(batches_sorted))
    course_field = f"""<input type="hidden" name="course" value="{e(c["title"])}">
<fieldset class="field"><legend>Which batch suits you?</legend>
{radios}
</fieldset>"""
    form = form_block("cd", course_field, "Demo class requested",
                      f'Thanks, <span data-success-name></span>. We will call you within one working day to fix a time for your {e(c["title"])} demo class.',
                      "Book my free demo class")

    ld = jsonld({
        "@context": "https://schema.org", "@type": "Course", "name": c["title"], "description": c["summary"],
        "provider": {"@type": "EducationalOrganization", "name": SITE["name"], "url": SITE["url"]},
        "hasCourseInstance": [{"@type": "CourseInstance", "courseMode": "onsite",
                               "startDate": f'2026-{MONTHS[b["month"]]:02d}-{int(b["day"]):02d}',
                               "courseSchedule": {"@type": "Schedule", "repeatFrequency": "P1W", "description": f'{b["days"]}, {b["time"]}'}}
                              for b in batches_sorted]})

    body = f"""<main id="main">
<nav class="breadcrumb container" aria-label="Breadcrumb"><ol>
<li><a href="{root}index.html">Home</a></li><li aria-hidden="true">/</li>
<li><a href="{root}courses.html">Courses</a></li><li aria-hidden="true">/</li>
<li aria-current="page">{e(c["title"])}</li>
</ol></nav>

<section class="course-hero container">
<div class="split">
<div>
<div class="kicker">{e(c["cat"])} course, taught on campus</div>
<h1 class="h-page">{e(c["title"])}</h1>
<p class="lead">{e(c["summary"])}</p>
<dl class="facts">
<div><dt>Duration</dt><dd>{e(c["duration"])}</dd></div>
<div><dt>Class time</dt><dd>{e(c["hours"])}</dd></div>
<div><dt>Level</dt><dd>{e(c["level"])}</dd></div>
<div><dt>Fee</dt><dd>{e(c["fee"])}</dd></div>
</dl>
<div class="btn-row">
<a class="btn btn--primary btn--lg" href="#enquire">Book a free demo class</a>
<a class="btn btn--outline btn--lg" href="#syllabus">See the syllabus</a>
</div>
</div>
<div class="board">
<div class="board__head"><h2 class="board__title">Upcoming batches</h2></div>
<ul class="board__list">
{board}
</ul>
<a class="btn btn--accent btn--block" href="#enquire">Reserve a seat</a>
</div>
</div>
</section>

<section class="section section--white">
<div class="container split">
<div>
<h2 class="h-section">What you will be able to do</h2>
<ul class="checklist checklist--grid" style="margin-top:28px">
{outcomes}
</ul>
</div>
<div class="aside-box">
<h2>Who this course is for</h2>
<ul>
{for_who}
</ul>
<h3>Before you start</h3>
<p>{e(c["prereq"])}</p>
</div>
</div>
</section>

<section id="syllabus" class="section container">
<div class="section-head">
<h2 class="h-section">Syllabus</h2>
<button type="button" class="btn btn--outline" data-expand-all aria-controls="syllabus-list" aria-expanded="false">Expand all</button>
</div>
<div id="syllabus-list" class="accordion syllabus">
{modules}
</div>
</section>

<section class="section section--navy">
<div class="container">
<h2 class="h-section">What you will build</h2>
<p class="section-intro" style="color:var(--navy-muted)">Each project is reviewed by your instructor and goes into your portfolio.</p>
<div class="grid-auto projects">
{projects}
</div>
<h3 style="margin:52px 0 0;font-size:20px">Tools you will use</h3>
<ul class="tools">{tools}</ul>
</div>
</section>

<section id="batches" class="section container">
<h2 class="h-section">Batches and timings</h2>
<p class="section-intro">Same syllabus, same instructors in every batch. Pick the timing that fits around your work or college.</p>
<div class="table-wrap">
<table class="data-table data-table--stack">
<caption class="visually-hidden">{e(c["title"])} batches</caption>
<thead><tr><th scope="col">Batch</th><th scope="col">Days</th><th scope="col">Time</th><th scope="col">Starts</th><th scope="col">Status</th></tr></thead>
<tbody>
{table}
</tbody>
</table>
</div>
</section>

<section id="fees" class="section section--white">
<div class="container split">
<div>
<h2 class="h-section">Fees</h2>
<div class="fee-options">
<div class="fee-option fee-option--main"><div class="fee-option__label">Pay in full</div><div class="fee-option__amount">{e(c["fee"])}</div><div class="fee-option__note">[Early payment discount, if any]</div></div>
<div class="fee-option"><div class="fee-option__label">Pay in instalments</div><div class="fee-option__amount">[n] × [amount]</div><div class="fee-option__note">[Instalment schedule]</div></div>
</div>
<h3 style="margin:30px 0 0;font-size:20px">The fee includes</h3>
<ul class="checklist checklist--grid" style="margin-top:14px;color:var(--ink-2)">
<li>{CHECK}All classes and lab sessions</li>
<li>{CHECK}Printed notes and practice sets</li>
<li>{CHECK}Open lab hours outside class</li>
<li>{CHECK}Completion certificate</li>
<li>{CHECK}Resume review and mock interviews</li>
<li>{CHECK}Access to hiring partner openings</li>
</ul>
</div>
<div>
<h2 class="h-card" style="font-size:28px">Your instructor</h2>
<div class="instructor">
<div class="photo-ph" role="img" aria-label="Photo placeholder: instructor portrait">[Portrait]</div>
<div class="person" style="margin:0">
<h3 style="margin-top:0">[Instructor name]</h3>
<div class="person__role">{e(c["instructorRole"])}</div>
<p>[Years] years working as {e(c["instructorJob"])} at [company]. Has taught [n] batches at {SITE["name"]}.</p>
</div>
</div>
</div>
</div>
</section>

<section id="enquire" class="section section--green on-dark">
<div class="container split split--form">
<div>
<h2 class="h-section">Try a class before you join</h2>
<p class="lead" style="margin-top:18px">Sit in on a live {e(c["title"])} session with the current batch. It is free, and there is no obligation to enroll.</p>
<div class="contact-links">
<a href="tel:{SITE["phone_href"]}">{PHONE}{SITE["phone_display"]}</a>
<a href="https://wa.me/{SITE["whatsapp"]}">{CHAT}Chat on WhatsApp</a>
</div>
</div>
{form}
</div>
</section>

<section class="section container">
<div class="section-head" style="align-items:baseline">
<h2 class="h-section" style="font-size:clamp(26px,4vw,40px)">Other courses</h2>
<a href="{root}courses.html" style="font-weight:700">See all courses</a>
</div>
<div class="grid-auto" style="margin-top:28px;gap:18px">
{related}
</div>
</section>
</main>
"""
    return page(f'{c["title"]} course — {SITE["name"]}', c["summary"][:155],
                f'courses/{c["slug"]}.html', root, "courses", body, extra_head=ld)


def build_policy(title, root=""):
    body = f"""<main id="main" class="section container" style="max-width:820px">
<h1 class="h-page">{title}</h1>
<p class="lead" style="margin-top:18px">[Add your {title.lower()} here. Ask your legal advisor to review it before publishing.]</p>
</main>
"""
    slug = "privacy.html" if "Privacy" in title else "refunds.html"
    return page(f'{title} — {SITE["name"]}', f'{SITE["name"]} {title.lower()}.', slug, root, "", body, cta_href="index.html#enquire")


FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect x="1" y="1" width="34" height="34" rx="6" fill="#1F4D3F"/><path d="M9 25V11l9 9 9-9v14" fill="none" stroke="#E8A317" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parent / "site"))
    out = Path(ap.parse_args().out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(HERE / "assets", out / "assets")
    (out / "assets" / "img").mkdir(exist_ok=True)
    (out / "assets" / "img" / "favicon.svg").write_text(FAVICON)
    (out / "courses").mkdir()
    (out / "index.html").write_text(build_home(), encoding="utf-8")
    (out / "courses.html").write_text(build_catalogue(), encoding="utf-8")
    for c in COURSES:
        (out / "courses" / f'{c["slug"]}.html').write_text(build_course(c), encoding="utf-8")
    (out / "privacy.html").write_text(build_policy("Privacy policy"), encoding="utf-8")
    (out / "refunds.html").write_text(build_policy("Refund policy"), encoding="utf-8")
    urls = ["", "courses.html"] + [f'courses/{c["slug"]}.html' for c in COURSES]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f'  <url><loc>{SITE["url"]}/{u}</loc></url>\n' for u in urls) + "</urlset>\n")
    (out / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n')
    print(f"Built {2 + len(COURSES) + 2} pages into {out}")


if __name__ == "__main__":
    main()
