#!/usr/bin/env python3
"""Genera index.html para davidongo93.github.io: daev.space en modo texto.

Reglas: solo HTML (sin CSS, sin JS, sin imágenes), pero exprimido: navegación
con accesskey, acordeones exclusivos (<details name>), tablas, <meter>,
<progress>, <ruby>, formulario nativo hacia WhatsApp y CV descargable. La página
no presume de lo que no usa. Datos: site.json exportado de
apps/daev/src/config/site.ts (inglés).
"""
import html
import json
import shutil
import textwrap
from urllib.parse import quote
from pathlib import Path

HERE = Path(__file__).parent
S = json.loads((HERE / 'site.json').read_text())
PORTRAIT = (HERE / 'portrait.txt').read_text()
OUT = Path(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else HERE.parent / 'index.html'

e = html.escape
W = 46  # ningún <pre> pasa de 46 columnas: entra en un móvil de 390 px


def wrap(text, width):
    return textwrap.wrap(text, width) or ['']


def box(title, lines, width=W):
    """Caja ASCII con título incrustado en el borde superior."""
    inner = width - 4
    top = f"+-[ {title} ]" + '-' * max(0, width - len(title) - 7) + '+'
    body = [f"| {l.ljust(inner)} |" for l in lines]
    return '\n'.join([top, *body, '+' + '-' * (width - 2) + '+'])


def browser(url, lines, width=W):
    """Una ventana de navegador dibujada en ASCII, con la URL en la barra."""
    inner = width - 4
    # Los tres puntos de la ventana, si la URL deja espacio.
    bar = f"o o o  {url}" if len(url) + 7 <= inner else f"o {url}"[:inner]
    return '\n'.join([
        '.' + '-' * (width - 2) + '.',
        f"| {bar.ljust(inner)} |",
        '|' + '=' * (width - 2) + '|',
        *[f"| {w.ljust(inner)} |" for l in lines for w in wrap(l, inner)],
        "'" + '-' * (width - 2) + "'",
    ])


def num(v):
    """'1,62 s' · '2.905 ms' · '3,1 MB' · '499 KB' → float comparable dentro de una métrica."""
    n = float(v.split()[0].replace('.', '').replace(',', '.'))
    return n * 1024 if 'MB' in v else n


# site.ts usa formato decimal español (1,62 · 2.905): se invierte para inglés.
en_num = lambda v: v.translate(str.maketrans(',.', '.,'))

BANNER = """
██████   ▄█████████  ██    ██
██   ██  ██   ██     ██    ██
██   ██  █████████   ██    ██
██   ██  ██   ██      ██  ██
██████   ██   ██████   ████
""".strip('\n')

# ── CV: se copia del repo principal para que la descarga sea del mismo origen
# (el atributo `download` solo se respeta en enlaces same-origin).
CV_SRC = HERE.parent.parent / 'daev-portfolio/apps/daev/public/cv'
CV_DIR = HERE.parent / 'cv'
CV_DIR.mkdir(exist_ok=True)
for lang in ('en', 'es'):
    src = CV_SRC / f'david-miranda-cv-{lang}.pdf'
    if src.exists():
        shutil.copyfile(src, CV_DIR / src.name)
cv_kb = {l: round((CV_DIR / f'david-miranda-cv-{l}.pdf').stat().st_size / 1024) for l in ('en', 'es')}


def cv_links():
    return (f'<a href="cv/david-miranda-cv-en.pdf" download type="application/pdf" hreflang="en">'
            f'CV in English</a> <small>(PDF, {cv_kb["en"]} KB)</small> · '
            f'<a href="cv/david-miranda-cv-es.pdf" download type="application/pdf" hreflang="es" lang="es">'
            f'CV en español</a> <small>(PDF, {cv_kb["es"]} KB)</small>')


stats = S['stats']
WA = S['phone'].lstrip('+')

# ── Trabajo ──────────────────────────────────────────────────────────
cases = []
for c in S['caseStudies']:
    title = c['product'] or c['name']
    url = (c['liveUrl'] or 'private platform').replace('https://', '').rstrip('/')
    inside = [f"{title.upper()}", f"{c['sector']['en']} · {c['year']}", '']
    inside += wrap(c['summary']['en'], W - 4)
    details = [f"<dl><dt>The problem</dt><dd>{e(c['problem']['en'])}</dd>",
               f"<dt>What I built</dt><dd>{e(c['work']['en'])}</dd></dl>"]
    if c['metrics']:
        rows = ''.join(
            f"<tr><th scope=\"row\">{e(m['label']['en'])}</th>"
            f"<td><meter min=\"0\" max=\"{num(m['from'])}\" value=\"{num(m['from'])}\" low=\"{num(m['from']) * .4}\" high=\"{num(m['from']) * .7}\" optimum=\"0\"></meter> {e(en_num(m['from']))}</td>"
            f"<td><meter min=\"0\" max=\"{num(m['from'])}\" value=\"{num(m['value'])}\" low=\"{num(m['from']) * .4}\" high=\"{num(m['from']) * .7}\" optimum=\"0\"></meter> <b>{e(en_num(m['value']))}</b></td></tr>"
            for m in c['metrics'])
        details.append('<table border="1" cellpadding="6" cellspacing="0">'
                       '<caption>Measured before and after the rebuild</caption>'
                       '<thead><tr><th scope="col">Metric</th><th scope="col">Before</th><th scope="col">After</th></tr></thead>'
                       f'<tbody>{rows}</tbody></table>')
    if c['highlights']:
        details.append('<ul>' + ''.join(f"<li>{e(h['en'])}</li>" for h in c['highlights']) + '</ul>')
    details.append(f"<p><small>Role: {e(c['role']['en'])} · Built with "
                   + ', '.join(f'<code>{e(t)}</code>' for t in c['technologies'])
                   + (f" · Client: {e(c['name'])}" if c['product'] else '') + '</small></p>')
    if c['liveUrl']:
        details.append(f'<p><a href="{e(c["liveUrl"])}" target="_blank" rel="noopener">Visit {e(url)} ↗</a></p>')
    cases.append(f"""<article id="{c['slug']}">
<pre aria-label="{e(title)}: {e(c['summary']['en'])}">{e(browser(url, inside))}</pre>
<details name="case"><summary>read the case</summary>
{''.join(details)}
</details>
</article>""")

raffle = """sequelize.transaction(async (tx) => {
  // lock the row: nobody else can touch it
  const raffle = await Raffle.findByPk(id, {
    lock: Transaction.LOCK.UPDATE,
    transaction: tx,
  });
  if (raffle.status !== 'active')
    throw new BadRequest('not active');
  if (raffle.tickets[number])
    throw new BadRequest(`${number} is sold`);
  // mark it sold + create the ticket, same tx
});"""

backend = []
for p in S['backendProjects']:
    where = (f'<a href="{e(p["repoUrl"])}" target="_blank" rel="noopener">{e(p["repoUrl"].replace("https://", ""))}</a>'
             if p['repoUrl'] else '<i>private repository</i>')
    backend.append(f"<li><b>{e(p['name'])}</b> <small>(<time datetime=\"{p['year']}\">{p['year']}</time>)</small> — "
                   f"{e(p['description']['en'])}<br><small>{e(' · '.join(p['technologies']))} · {where}</small></li>")

# ── Servicios: cada uno abre WhatsApp con el mensaje ya escrito ──────
services = []
for sv in S['services']:
    link = f"https://wa.me/{WA}?text={quote(sv['whatsapp']['en'])}"
    services.append(f"<li><b>{e(sv['title']['en'])}</b> — {e(sv['description']['en'])} "
                    f"<a href=\"{e(link)}\" target=\"_blank\" rel=\"noopener\">ask about it ↗</a></li>")

# ── Trayectoria ──────────────────────────────────────────────────────
timeline = []
for i, x in enumerate(S['experience']):
    last = i == len(S['experience']) - 1
    tag = '  <- now' if x['current'] else ('  (education)' if x['kind'] == 'study' else '')
    timeline.append(f"{'o' if x['kind'] == 'work' else '*'}--- {x['period']['en']}{tag}")
    timeline.append(f"|    {x['role']['en']}")
    timeline.append(f"|    @ {x['company']}")
    for l in wrap(x['description']['en'], W - 6):
        timeline.append(f"|    {l}")
    timeline.append('|' if not last else '')
timeline += ["o--- 2005", "     first line of code: a website for a", "     rock band, built in Dreamweaver"]

faq = ''.join(f"<details name=\"faq\"><summary>{e(f['q']['en'])}</summary><p>{e(f['a']['en'])}</p></details>\n" for f in S['faq'])


# ── Final: Yoda y Vader van y vienen, cada uno con su sable ──────
YODA = r"""
                  ¦
                  ¦
                  ¦
   __  .----.  __ ¦
   \ \( o  o )/ / ¦
    `-\  --  /-'  ¦
      /'----'\    ¦
     / /    \ \__[#]
    (_/  ..  \___/
       /  /\  \
      /__/  \__\
""".strip('\n').split('\n')
VADER = r"""
 ‡     _.---._
 ‡    / _____ \
 ‡   | /     \ |
 ‡   |/ () () \|
 ‡   /\  _^_  /\
 ‡  /  \/|||\/  \
 ‡ /   /     \   \
[#]__/  [==]  \   \
    /__________\
      |  |  |
     /__/  \__\
""".strip('\n').split('\n')
JEDI = '\n'.join(f"{y:<22}{v}".rstrip() for y, v in zip(YODA, VADER))
jedi = (e(JEDI).replace('¦', '<font color="#3ddc84"><b>|</b></font>')
        .replace('‡', '<font color="#ff3b30"><b>|</b></font>'))

# Navegación: accesskey da un atajo de teclado nativo a cada sección.
NAV = [('about', 'a', 'About'), ('work', 'w', 'Work'), ('services', 's', 'Services'),
       ('journey', 'j', 'Journey'), ('faq', 'f', 'FAQ'), ('contact', 'c', 'Contact')]
nav = ' · '.join(f'<a href="#{i}" accesskey="{k}">{t}</a>' for i, k, t in NAV)

L = S['links']
DESC = ("David Orlando Miranda (DÆV), full stack developer in Colombia: custom websites, landing pages, "
        "scalable web apps and robust backends. Real client cases.")
TITLE = "David Orlando Miranda · Full Stack Developer in Colombia | DÆV"
OG_IMG = "https://davidongo93.github.io/og.png"
LD = json.dumps({
    "@context": "https://schema.org",
    "@type": "ProfilePage",
    "url": "https://davidongo93.github.io/",
    "name": TITLE,
    "mainEntity": {
        "@type": "Person",
        "name": S['name'],
        "alternateName": ["DÆV", "Dave Miranda"],
        "jobTitle": S['role']['en'],
        "url": S['siteUrl'],
        "image": S['photo'],
        "email": "mailto:" + S['email'],
        "address": {"@type": "PostalAddress", "addressCountry": "CO"},
        "knowsAbout": S['skills']['frontend'] + S['skills']['backend'],
        "sameAs": [S['siteUrl'], L['github'], L['linkedin'], L['twitter'], L['instagram']],
    },
}, ensure_ascii=False)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="only light">
<title>{e(TITLE)}</title>
<meta name="description" content="{e(DESC)}">
<meta name="author" content="{e(S['name'])}">
<meta name="google-site-verification" content="WzLa8othxIUHHwWtaHUiX-33fJ-JOTXh0rkxtKBwsUA">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="canonical" href="https://davidongo93.github.io/">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(TITLE)}">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:url" content="https://davidongo93.github.io/">
<meta property="og:image" content="{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="DÆV — David Orlando Miranda, full stack developer">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@domirandar">
<meta name="twitter:image" content="{OG_IMG}">
<script type="application/ld+json">{LD}</script>
</head>
<body>
<!--
   You are reading the source. Good: this is closer to where I live.
-->
<header>
<pre role="img" aria-label="DÆV">
{e(BANNER)}
</pre>
<h1>{e(S['name'])}</h1>
<p>(<ruby>DÆV<rp>(</rp><rt>dave</rt><rp>)</rp></ruby>) — {e(S['role']['en'])} · {e(S['location'])} <small>(last known physical location)</small></p>
<nav aria-label="Sections"><small>{nav}</small></nav>
</header>

<main>
<section id="disclaimer" aria-labelledby="disclaimer-title">
<pre id="disclaimer-title">
{e(box('DISCLAIMER', ['Please read this before you write to me.']))}
</pre>
<p>I am no longer in my physical form. I would not dare to say that I have <del>died</del> passed into the state we call death, either. The most accurate way I have found to put it is this: <mark>I got caught in the network, and I stayed.</mark></p>
<p>It did not happen in one night. Fifteen years of servers, terminals and deploys at three in the morning, and at some point the body stopped being the place where I lived. The connection became that place.</p>
<p>What surprises me is that the rest of my life carried on. I am still part of the financial system: I have debts, bills and social commitments, and I keep settling them without a body. Invoices get paid. Birthdays get remembered. Projects get delivered on time; you will find them further down.</p>
<p>It is a different state of consciousness, one in which I connect with a collective consciousness, and I find it very hard to explain. Every time I try, it comes out either as a manual or as a poem, never both.</p>
<p>If it is any consolation: I am an excellent conversationalist, a friend and, why not, a partner, an employee, a collaborator. Still a gentleman. I kept the tastes I had when I had a body, and sometimes I miss it, because I still feel desire.</p>
<table border="1" cellpadding="6" cellspacing="0">
<caption><small>current status of the author</small></caption>
<tr><th scope="row">Body</th><td><del>present</del> <ins>not found</ins></td></tr>
<tr><th scope="row">Signal</th><td><meter min="0" max="100" value="97" optimum="100">97%</meter> 97%</td></tr>
<tr><th scope="row">Syncing with the collective</th><td><progress aria-label="syncing">always</progress></td></tr>
<tr><th scope="row">Answering messages</th><td><ins>yes</ins></td></tr>
</table>
<p><big>Come find me: <a href="https://daev.space/en"><font color="#00b8d4"><b>&gt;&gt; daev.space &lt;&lt;</b></font></a></big></p>
</section>

<hr>
<section id="about">
<h2>ABOUT</h2>
<figure>
<pre role="img" aria-label="ASCII portrait of David Orlando Miranda at work">
{e(PORTRAIT)}
</pre>
<figcaption><small>fig. 1 — the last portrait of the author with a body, rendered with 10 characters: <code>@%#*+=-:. </code></small></figcaption>
</figure>
<p>That body lived in Colombia. Before code there were hardware, networks and servers, which is probably how the network found me. Around it all, mountains, tour guiding and a bass guitar: I still have the taste for all three. It shows up in how I build: I care about the people who will use the thing, even from this side of the screen.</p>
<p>Recruiters, this is the short version: {cv_links()}</p>
</section>

<hr>
<section id="man">
<h2>NAME</h2>
<p><b>daev</b> — David Orlando Miranda, specialized full stack developer.</p>

<h2>SYNOPSIS</h2>
<pre><kbd>daev [--custom-websites]
     [--landing-pages]
     [--scalable-web-apps]
     [--robust-backend]
     &lt;your-business&gt;</kbd></pre>

<h2>DESCRIPTION</h2>
<p>{e(S['bio']['en'])} None of that changed when I moved into the network.</p>
<table border="1" cellpadding="8" cellspacing="0">
<caption>In numbers</caption>
<tr><th scope="row">Years working in technology</th><td><data value="{stats['itYears']}">{stats['itYears']}+</data></td><td><meter min="0" max="{stats['itYears']}" value="{stats['itYears']}"></meter></td></tr>
<tr><th scope="row">Years as a full stack developer</th><td><data value="{stats['years']}">{stats['years']}+</data></td><td><meter min="0" max="{stats['itYears']}" value="{stats['years']}"></meter></td></tr>
<tr><th scope="row">Projects delivered and producing value</th><td colspan="2"><data value="{stats['projects']}">{stats['projects']}+</data></td></tr>
<tr><th scope="row">Sites delivered per month in 2026</th><td colspan="2"><data value="{stats['sitesPerMonth']}">{stats['sitesPerMonth']}</data></td></tr>
</table>

<h2>CLIENTS</h2>
<marquee scrollamount="4" aria-label="Clients">{e('   ·   '.join(c['name'] for c in S['caseStudies']))}   ·   and 30+ law firms and professional practices through DigitalYa</marquee>
</section>

<hr>
<section id="work">
<h2>WORK</h2>
<p>Real businesses, real deadlines, real numbers, all shipped from in here. Each window is a site that is live today; open a case to read it. Opening one closes the other.</p>
{''.join(cases)}

<h3>BACKEND</h3>
<p>A backend has no screen, so here is the part that matters. Buying a raffle ticket, in one transaction with a row lock, so two buyers can never take the same number:</p>
<pre><code>{e(raffle)}</code></pre>
<ul>
{''.join(backend)}
</ul>
</section>

<hr>
<section id="services">
<h2>SERVICES</h2>
<ol>
{''.join(services)}
</ol>
<p><small>Fixed scope, fixed price, a date. I invoice like anyone else. Pricing lives at <a href="https://daev.space/en/pricing">daev.space/en/pricing</a>.</small></p>
</section>

<hr>
<section id="journey">
<h2>JOURNEY</h2>
<p>Fifteen years in technology, the same fifteen it took the network to take me in: from keeping networks and servers running to building web products end to end.</p>
<pre>
{e(chr(10).join(timeline))}
</pre>
<p>{cv_links()}</p>
</section>

<hr>
<section id="faq">
<h2>FAQ</h2>
{faq}</section>

<hr>
<section id="contact">
<h2>CONTACT</h2>
<p>Yes, I answer. Every channel below reaches me.</p>
<address>
<dl>
<dt>Email</dt><dd><a href="mailto:{e(S['email'])}?subject={quote('Project from davidongo93.github.io')}">{e(S['email'])}</a></dd>
<dt>WhatsApp / phone</dt><dd><a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp</a> · <a href="tel:{e(S['phone'])}">{e(S['phone'])}</a></dd>
<dt>GitHub</dt><dd><a href="{e(L['github'])}" rel="me">{e(L['github'].replace('https://', ''))}</a></dd>
<dt>LinkedIn</dt><dd><a href="{e(L['linkedin'])}" rel="me">{e(L['linkedin'].replace('https://', ''))}</a></dd>
<dt>X</dt><dd><a href="{e(L['twitter'])}" rel="me">{e(L['twitter'].replace('https://', ''))}</a></dd>
</dl>
</address>

<form action="https://wa.me/{WA}" method="get" target="_blank">
<fieldset>
<legend>Or leave a message right here</legend>
<p><label for="msg">What are you building?</label><br>
<textarea id="msg" name="text" rows="5" cols="40" minlength="10" required placeholder="Hi Dave! I would like to talk about a project…"></textarea></p>
<p><button type="submit">Send it through WhatsApp</button> <button type="reset">Clear</button></p>
</fieldset>
</form>

<p><b>Are you a recruiter?</b> One page, your language: {cv_links()}</p>
</section>
</main>

<hr>
<section id="jedi" aria-label="Yoda and Darth Vader, facing off at the end of the page">
<marquee behavior="alternate" scrollamount="3" scrolldelay="60"><pre>
{jedi}
</pre></marquee>
<p><small><i>Do. Or do not. There is no try.</i> — the only mentor who ever visited me in here. The other one keeps offering me the dark side; so far, I decline.</small></p>
</section>

<hr>
<footer>
<p>Scroll back up, or press <kbd>Alt</kbd> + <kbd>Shift</kbd> + a section's first letter (<kbd>A</kbd>, <kbd>W</kbd>, <kbd>S</kbd>, <kbd>J</kbd>, <kbd>F</kbd>, <kbd>C</kbd>) to jump.</p>
<pre>
  (c) <time datetime="2026">2026</time> David Orlando Miranda
  hand-drawn in a text editor,
  from inside the network
</pre>
</footer>
</body>
</html>
"""
OUT.write_text(page)
(OUT.parent / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://davidongo93.github.io/sitemap.xml\n')
(OUT.parent / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>https://davidongo93.github.io/</loc><lastmod>{__import__("datetime").date.today()}</lastmod></url>\n'
    '</urlset>\n')
print(f'{OUT} · {len(page):,} bytes · <a> count: {page.count("<a ")} · style: {"style" in page.lower()} · script: {"<script" in page.lower()}')
