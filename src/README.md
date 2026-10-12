# Northfield Academy website

A fully responsive, static multi-page site for an academy that runs in-person courses.
No framework and no build dependencies: plain HTML, CSS and a small vanilla JS file.
It deploys anywhere (Netlify, Vercel, Cloudflare Pages, S3, cPanel hosting).

## Structure

```
src/
  build.py          Generates every page from shared partials + courses.json
  courses.json      All course content (syllabus, batches, projects, tools…)
  assets/css/styles.css
  assets/js/main.js
site/               Generated output — this is what you deploy
  index.html        Home
  courses.html      Catalogue with subject + timing filters and a comparison table
  courses/<slug>.html   One page per course (6)
  privacy.html, refunds.html, sitemap.xml, robots.txt
```

## Editing

1. Change course content in `src/courses.json` (add a course by adding an object with a new `slug`).
2. Change contact details, domain and form endpoint at the top of `src/build.py` (`SITE = {…}`).
3. Run `python3 src/build.py` — it rewrites `site/`.

Replace everything in [square brackets] (fees, phone, address, instructor names, student quotes)
and swap the striped `.photo-ph` placeholders for real `<img>` tags (put images in `site/assets/img/`,
or better, add them to `src/assets/img/` so rebuilds keep them).

## Enquiry forms

Forms validate on the client and show a confirmation. To actually receive enquiries, set
`form_endpoint` in `SITE` to a URL that accepts a JSON POST — e.g. Formspree, a Netlify/Vercel
function, or your CRM webhook. Payload: `name, phone, email, course, timing|batch, page`.

## Responsive behaviour

Mobile-first CSS, tested with no horizontal overflow at 320, 360, 414, 600, 768, 1024, 1280, 1440 and 1920px.
- Header: hamburger menu below 880px (Esc closes it, auto-closes when widened); demo-class CTA shows from 1240px.
- Filter chips scroll horizontally on phones instead of wrapping into a tall block.
- Comparison and batch tables turn into stacked cards below 680px.
- Hero, campus, fees and enquiry sections go from two columns to one below 960px.
- Fluid type with `clamp()`; touch targets are at least 44px.

## Accessibility and SEO

Skip link, visible focus rings, `aria-pressed` filters with a live result count, native `<details>`
accordions, labelled form fields with focused error messages, `prefers-reduced-motion` respected.
Each page has a unique title, meta description, canonical URL and Open Graph tags; JSON-LD for
EducationalOrganization, FAQPage, ItemList and Course (with CourseInstance start dates). Sitemap and robots.txt included.
