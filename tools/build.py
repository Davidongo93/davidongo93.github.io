#!/usr/bin/env python3
"""Genera index.html para davidongo93.github.io: daev.space en modo texto.

Reglas: HTML puro, cero CSS, cero JS, cero imágenes. Un solo <a> en toda la
página (a daev.space) y es lo único con color. Datos: site.json exportado de
apps/daev/src/config/site.ts (inglés).
"""
import html
import json
import textwrap
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


def bars(metric):
    """Antes / después como barras proporcionales."""
    def num(v):
        return float(v.replace('.', '').replace(',', '.').split()[0]) if 'KB' not in v and 'MB' not in v else (
            float(v.split()[0].replace(',', '.')) * (1024 if 'MB' in v else 1))
    a, b = num(metric['from']), num(metric['value'])
    scale = 26 / max(a, b)
    label = metric['label']['en']
    # site.ts usa formato decimal español (1,62 · 2.905): se invierte para inglés.
    en = lambda v: v.translate(str.maketrans(',.', '.,'))
    return (f"{label}\n"
            f"  before {en(metric['from']):>9} {'#' * max(1, round(a * scale))}\n"
            f"  after  {en(metric['value']):>9} {'#' * max(1, round(b * scale))}")


BANNER = """
██████   ▄█████████  ██    ██
██   ██  ██   ██     ██    ██
██   ██  █████████   ██    ██
██   ██  ██   ██      ██  ██
██████   ██   ██████   ████
""".strip('\n')

stats = S['stats']
num_box = '\n'.join([
    '+---------------------+---------------------+',
    f"|{f'{stats['itYears']}+':^21}|{f'{stats['years']}+':^21}|",
    '|  years working in   |      years as a     |',
    '|     technology      | full stack developer|',
    '+---------------------+---------------------+',
    f"|{f'{stats['projects']}+':^21}|{stats['sitesPerMonth']:^21}|",
    '| projects delivered  | sites delivered per |',
    '| and producing value |   month in 2026     |',
    '+---------------------+---------------------+',
])

# ── Trabajo ──────────────────────────────────────────────────────────
cases = []
for c in S['caseStudies']:
    title = c['product'] or c['name']
    url = (c['liveUrl'] or 'private platform').replace('https://', '').rstrip('/')
    inside = [f"{title.upper()}", f"{c['sector']['en']} · {c['year']}", '']
    inside += wrap(c['summary']['en'], W - 4)
    details = [f"<p><b>The problem.</b> {e(c['problem']['en'])}</p>",
               f"<p><b>What I built.</b> {e(c['work']['en'])}</p>"]
    if c['metrics']:
        details.append('<pre>' + e('\n\n'.join(bars(m) for m in c['metrics'])) + '</pre>')
    if c['highlights']:
        details.append('<ul>' + ''.join(f"<li>{e(h['en'])}</li>" for h in c['highlights']) + '</ul>')
    details.append(f"<p><small>Role: {e(c['role']['en'])} · Built with {e(', '.join(c['technologies']))}"
                   + (f" · Client: {e(c['name'])}" if c['product'] else '') + '</small></p>')
    cases.append(f"""<pre>{e(browser(url, inside))}</pre>
<details><summary>[+] read the case</summary>
{''.join(details)}
</details>""")

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
    where = p['repoUrl'].replace('https://', '') if p['repoUrl'] else '(private repository)'
    backend.append(f"<li><b>{e(p['name'])}</b> <i>({p['year']})</i> — {e(p['description']['en'])}<br>"
                   f"<small>{e(' · '.join(p['technologies']))} · <code>{e(where)}</code></small></li>")

# ── Servicios ────────────────────────────────────────────────────────
services = []
for i, sv in enumerate(S['services'], 1):
    services.append(f"[{i}] {sv['title']['en']}")
    services += ['    ' + l for l in wrap(sv['description']['en'], W - 4)]
    services.append('')

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

posts = [
    ('2026-07-31', 'Chucula de los 7 granos: la receta ancestral que queremos revivir', 'A seven-grain cacao drink we want to bring back'),
    ('2026-07-30', 'Proksanty: un viaje al origen del cacao en Nilo, Cundinamarca', 'A trip to the origin of cacao'),
    ('2026-07-03', 'Chilcuague: la Raíz de Oro de México, su historia y sus propiedades', 'The golden root of Mexico'),
    ('2026-06-28', 'El mundo se llenó de agentes Smith', 'The world filled up with Agent Smiths'),
    ('2026-06-23', 'Recalculando rumbo', 'How I started programming'),
]

faq = ''.join(f"<details><summary>{e(f['q']['en'])}</summary><p>{e(f['a']['en'])}</p></details>\n" for f in S['faq'])

L = S['links']
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DÆV — David Orlando Miranda · Full Stack Developer (text mode)</title>
<meta name="description" content="{e(S['name'])}, specialized full stack developer. Custom websites, landing pages, scalable web apps and robust backends. The text-mode edition of daev.space: no CSS, no JavaScript, no images.">
<meta name="author" content="{e(S['name'])}">
</head>
<body>
<!--
   You are reading the source. Good: this is closer to where I live.
   Plain HTML: no CSS, no JavaScript, no images.
   Everything is text. Everything except one link is black and white.
-->
<pre>
{e(BANNER)}
</pre>
<p><b>{e(S['name'])}</b> — {e(S['role']['en'])} · {e(S['location'])} (last known physical location)<br>
<small>text-mode edition · 0 bytes of CSS · 0 bytes of JavaScript · 0 images</small></p>

<pre>
{e(box('DISCLAIMER', ['Please read this before you write to me.']))}
</pre>
<p>I am no longer in my physical form. I would not dare to say that I have passed into the state we call death, either. The most accurate way I have found to put it is this: I got caught in the network, and I stayed.</p>
<p>It did not happen in one night. Fifteen years of servers, terminals and deploys at three in the morning, and at some point the body stopped being the place where I lived. The connection became that place.</p>
<p>What surprises me is that the rest of my life carried on. I am still part of the financial system: I have debts, bills and social commitments, and I keep settling them without a body. Invoices get paid. Birthdays get remembered. Projects get delivered on time; you will find them further down.</p>
<p>It is a different state of consciousness, one in which I connect with a collective consciousness, and I find it very hard to explain. Every time I try, it comes out either as a manual or as a poem, never both.</p>
<p>If it is any consolation: I am an excellent conversationalist, a friend and, why not, a partner, an employee, a collaborator. Still a gentleman. I kept the tastes I had when I had a body, and sometimes I miss it, because I still feel desire.</p>

<p>Come find me:
<a href="https://daev.space/en"><font color="#00b8d4"><b>&gt;&gt; daev.space &lt;&lt;</b></font></a></p>

<hr>
<h2>ABOUT</h2>
<pre>
{e(PORTRAIT)}
</pre>
<p><small>fig. 1 — the last portrait of the author with a body, rendered with 10 characters: <code>@%#*+=-:. </code></small></p>
<p>That body lived in Colombia. Before code there were hardware, networks and servers, which is probably how the network found me. Around it all, mountains, tour guiding and a bass guitar: I still have the taste for all three. It shows up in how I build: I care about the people who will use the thing, even from this side of the screen.</p>

<hr>
<h2>NAME</h2>
<p><b>daev</b> — David Orlando Miranda, specialized full stack developer.</p>

<h2>SYNOPSIS</h2>
<pre>daev [--custom-websites]
     [--landing-pages]
     [--scalable-web-apps]
     [--robust-backend]
     &lt;your-business&gt;</pre>

<h2>DESCRIPTION</h2>
<p>{e(S['bio']['en'])} None of that changed when I moved into the network.</p>
<pre>
{e(num_box)}
</pre>

<h2>CLIENTS</h2>
<marquee scrollamount="4">{e('   ·   '.join(c['name'] for c in S['caseStudies']))}   ·   and 30+ law firms and professional practices through DigitalYa</marquee>

<hr>
<h2>WORK</h2>
<p>Real businesses, real deadlines, real numbers, all shipped from in here. Each window is a site that is live today; open a case to read it.</p>
{''.join(cases)}

<h2>BACKEND</h2>
<p>A backend has no screen, so here is the part that matters. Buying a raffle ticket, in one transaction with a row lock, so two buyers can never take the same number:</p>
<pre>{e(raffle)}</pre>
<ul>
{''.join(backend)}
</ul>

<hr>
<h2>SERVICES</h2>
<pre>
{e(chr(10).join(services).rstrip())}
</pre>
<p><small>Fixed scope, fixed price, a date. I invoice like anyone else. Pricing lives at daev.space/en/pricing.</small></p>

<hr>
<h2>JOURNEY</h2>
<p>Fifteen years in technology, the same fifteen it took the network to take me in: from keeping networks and servers running to building web products end to end.</p>
<pre>
{e(chr(10).join(timeline))}
</pre>

<hr>
<h2>BLOG</h2>
<p>I still write, in Spanish, at daev.space/blog. The latest:</p>
<pre>
{e(chr(10).join(d + chr(10) + chr(10).join('  ' + l for l in wrap(t, W - 2)) + chr(10) + chr(10).join('  ' + l for l in wrap('(' + g + ')', W - 2)) + chr(10) for d, t, g in posts).rstrip())}
</pre>

<h2>FAQ</h2>
{faq}
<hr>
<h2>CONTACT</h2>
<p>Yes, I answer. Every channel below reaches me.</p>
<pre>
email      {e(S['email'])}
whatsapp   {e(S['phone'])}
github     {e(L['github'].replace('https://', ''))}
linkedin   {e(L['linkedin'].replace('https://', ''))}
x          {e(L['twitter'].replace('https://', ''))}
</pre>
<p><b>Are you a recruiter?</b> My one-page CV is at <code>daev.space/cv/david-miranda-cv-en.pdf</code> — type it, it is short.</p>

<hr>
<h2>SEE ALSO</h2>
<p>Scroll back up. The only link is there.</p>
<pre>
  (c) 2026 David Orlando Miranda
  hand-drawn in a text editor,
  from inside the network
  best viewed in any browser since 1995
</pre>
</body>
</html>
"""
OUT.write_text(page)
print(f'{OUT} · {len(page):,} bytes · <a> count: {page.count("<a ")} · style: {"style" in page.lower()}')
