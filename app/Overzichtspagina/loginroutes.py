"""Login- en registratieroutes voor de Overzichtspagina."""

from flask import flash, redirect, render_template, request, session, url_for

from app.db import execute_query
from app.Overzichtspagina import bp


def is_admin():
    """
    Controleer of de ingelogde gebruiker admin is.
    """
    return session.get("role") == "admin"


@bp.before_request
def require_login():
    """
    Bescherm de projectenpagina zolang de gebruiker niet is ingelogd.
    """
    # Routes die toegankelijk moeten zijn zonder inlog
    allowed_routes = {"projects.login", "projects.register", "projects.logout"}

    if request.endpoint in allowed_routes:
        return None

    if session.get("user_id"):
        return None

    flash("Log eerst in om je projecten te bekijken.", "error")
    return redirect(url_for("projects.login"))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Laat gebruiker inloggen.
    """

    if request.method == 'POST':
        # Haal inloggegevens uit formulier
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        # Controleer of beide velden ingevuld zijn
        if not username_or_email or not password:
            flash("Vul alle velden in.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        # Controleer zowel email als gebruikersnaam voor flexibel inloggen
        query = "SELECT * FROM users WHERE email = ? OR name = ? LIMIT 1"
        result = execute_query(query, [username_or_email, username_or_email])

        # Controleer of gebruiker in database werd gevonden
        if not isinstance(result, list) or not result:
            flash("Gebruikersnaam of wachtwoord is onjuist.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        user = result[0]

        # WAARSCHUWING: Dit is plaintext password vergelijking. In productie: use hashing!
        if user['password_hash'] != password:
            flash("Gebruikersnaam of wachtwoord is onjuist.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        # Sla gebruikersdata in sessie op zodat gebruiker ingelogd blijft
        session['user_id'] = user['user_id']
        session['name'] = user['name']
        session['role'] = user['role']

        flash("Succesvol ingelogd.", "success")

        # doorsturen naar projectenpagina
        return redirect(url_for('projects.overview'))

    # GET request - toon loginformulier
    return render_template('loginpage.html', username_or_email='')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Maak een nieuw normaal gebruikersaccount aan.
    """

    if request.method == 'POST':
        # Haal ingevulde gegevens uit formulier
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Controleer of alle velden ingevuld zijn
        if not name or not email or not password:
            flash("Vul alle velden in.", "error")
            return render_template('registerpage.html', name=name, email=email)

        # Controleer zowel email als gebruikersnaam om duplicaten te voorkomen
        query = "SELECT * FROM users WHERE email = ? OR name = ? LIMIT 1"
        existing_user = execute_query(query, [email, name])

        if isinstance(existing_user, list) and existing_user:
            flash("Deze gebruikersnaam of dit e-mailadres bestaat al.", "error")
            return render_template('registerpage.html', name=name, email=email)

        # Voeg nieuwe gebruiker in in de database met standaard rol "user"
        query = "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)"
        execute_query(query, [name, email, password, "user"])

        flash("Account aangemaakt. Je kunt nu inloggen.", "success")
        return redirect(url_for('projects.login'))

    # GET request - toon registratieformulier
    return render_template('registerpage.html', name='', email='')


@bp.route('/account', methods=['GET', 'POST'])
def account():
    """
    Laat de ingelogde gebruiker zijn wachtwoord wijzigen of account verwijderen.
    """
    # Haal user_id uit sessie (set door require_login())
    user_id = session.get('user_id')
    # Haal gebruikersgegevens op uit database
    query = "SELECT * FROM users WHERE user_id = ? LIMIT 1"
    result = execute_query(query, [user_id])

    # Controleer of gebruiker bestaat (account kan sinds login verwijderd zijn)
    if not isinstance(result, list) or not result:
        session.clear()
        flash("Je account is niet gevonden.", "error")
        return redirect(url_for('projects.login'))

    user = result[0]

    if request.method == 'POST':
        # Bepaal welke actie gebruiker wil uitvoeren
        action = request.form.get('action')

        if action == 'change_password':
            # Gebruiker wil wachtwoord wijzigen
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')

            # Controleer of beide wachtwoorden ingevuld zijn
            if not current_password or not new_password:
                flash("Vul je huidige en nieuwe wachtwoord in.", "error")
                return render_template('accountpage.html', user=user)

            # Verifieer het huidige wachtwoord (WAARSCHUWING: plaintext!)
            if user['password_hash'] != current_password:
                flash("Je huidige wachtwoord klopt niet.", "error")
                return render_template('accountpage.html', user=user)

            # Werk wachtwoord bij in database
            query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
            execute_query(query, [new_password, user_id])
            flash("Je wachtwoord is gewijzigd.", "success")
            return redirect(url_for('projects.account'))

        if action == 'delete_account':
            # Gebruiker wil account verwijderen - check eerst of er projecten aan gekoppeld zijn
            check_query = "SELECT COUNT(*) as count FROM testflow WHERE user_id = ?"
            check_result = execute_query(check_query, [user_id])

            # Controleer of gebruiker nog actieve projecten heeft
            if isinstance(check_result, list) and check_result and check_result[0].get('count', 0) > 0:
                flash("Je account kan niet worden verwijderd omdat er nog projecten aan gekoppeld zijn.", "error")
                return render_template('accountpage.html', user=user)

            # Verwijder account uit database
            delete_query = "DELETE FROM users WHERE user_id = ?"
            delete_result = execute_query(delete_query, [user_id])

            # Controleer op databasefouten
            if isinstance(delete_result, dict) and (delete_result.get("error") or delete_result.get("reason")):
                flash("Je account kon niet worden verwijderd. Probeer het opnieuw.", "error")
                return render_template('accountpage.html', user=user)

            # Account succesvol verwijderd - log uit en ga naar login
            session.clear()
            flash("Je account is verwijderd.", "success")
            return redirect(url_for('projects.login'))

    # GET request - toon accountpagina met huidig gebruikersdata
    return render_template('accountpage.html', user=user)


@bp.route('/logout')
def logout():
    """
    Log gebruiker uit.
    """
    # Verwijder alle sessiegegevens zodat gebruiker uitgelogd is
    session.clear()

    flash("Je bent uitgelogd.", "success")

    # Stuur terug naar loginpagina
    return redirect(url_for('projects.login'))
