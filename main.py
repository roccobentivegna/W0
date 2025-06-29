from flask import Flask, render_template, request, redirect, url_for, session
import random
import time

app = Flask(__name__)
app.secret_key = 'la-tua-chiave-segreta-qui'  # Assicurati di usare una chiave segreta sicura

# Lista temi disponibili: ogni tema è un dizionario con colori sfondo e testo
THEMES = [
    {'bg': 'white', 'fg': 'black'},
    {'bg': 'red', 'fg': 'black'},
    {'bg': 'red', 'fg': 'white'},
    {'bg': 'gray', 'fg': 'black'},
    {'bg': 'magenta', 'fg': 'black'},
    {'bg': 'black', 'fg': 'limegreen'},
    {'bg': 'black', 'fg': 'magenta'},
    {'bg': 'black', 'fg': 'white'},
    {'bg': 'yellow', 'fg': 'black'},
    {'bg': 'blue', 'fg': 'white'},
]


@app.route('/')
def index():
    # Scegli un tema casuale diverso dall'attuale, se c'è già
    current_theme = session.get('theme')
    new_theme = random.choice(THEMES)
    while current_theme == new_theme:
        new_theme = random.choice(THEMES)
    session['theme'] = new_theme
    return render_template('w0_intro.html', theme=new_theme)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    theme = session.get('theme', THEMES[0])  # tema di default se non c'è
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        fear = request.form['fear']

        responses = [name, year, fear]
        random.shuffle(responses)
        password = ''.join(responses).strip().lower()

        session['password'] = password
        session['quiz_completed'] = True
        session['user_name'] = name  # salva nome utente in sessione

        return redirect(url_for('message'))

    return render_template('quiz.html', theme=theme)


@app.route('/message')
def message():
    if not session.get('quiz_completed'):
        return redirect(url_for('quiz'))

    theme = session.get('theme', THEMES[0])
    return render_template('w0_message.html', theme=theme)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('quiz_completed'):
        return redirect(url_for('quiz'))

    if 'password' not in session:
        session.clear()
        return redirect(url_for('quiz'))

    if 'expiry' not in session:
        session['expiry'] = time.time() + 60  # 60 secondi da ora

    if time.time() > session.get('expiry', 0):
        session.clear()
        return redirect(url_for('quiz'))

    theme = session.get('theme', THEMES[0])

    if request.method == 'POST':
        entered = request.form['password'].strip().lower()
        if entered == session.get('password'):
            return redirect(url_for('secret'))
        else:
            remaining_time = max(0, session['expiry'] - time.time())
            return render_template('login.html', error=True, remaining_time=remaining_time, theme=theme)

    remaining_time = max(0, session['expiry'] - time.time())
    return render_template('login.html', error=False, remaining_time=remaining_time, theme=theme)


@app.route('/secret')
def secret():
    user_name = session.get('user_name', 'utente')
    theme = session.get('theme', THEMES[0])
    session.clear()
    return render_template('secret.html', user_name=user_name, theme=theme)
