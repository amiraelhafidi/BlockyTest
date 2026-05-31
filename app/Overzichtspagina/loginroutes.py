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

        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash("Vul alle velden in.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        query = "SELECT * FROM users WHERE email = ? OR name = ? LIMIT 1"
        result = execute_query(query, [username_or_email, username_or_email])

        if not isinstance(result, list) or not result:
            flash("Gebruikersnaam of wachtwoord is onjuist.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        user = result[0]

        if user['password_hash'] != password:
            flash("Gebruikersnaam of wachtwoord is onjuist.", "error")
            return render_template('loginpage.html', username_or_email=username_or_email)

        session['user_id'] = user['user_id']
        session['name'] = user['name']
        session['role'] = user['role']

        flash("Succesvol ingelogd.", "success")

        # doorsturen naar projectenpagina
        return redirect(url_for('projects.overview'))

    return render_template('loginpage.html', username_or_email='')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Maak een nieuw normaal gebruikersaccount aan.
    """

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash("Vul alle velden in.", "error")
            return render_template('registerpage.html', name=name, email=email)

        query = "SELECT * FROM users WHERE email = ? OR name = ? LIMIT 1"
        existing_user = execute_query(query, [email, name])

        if isinstance(existing_user, list) and existing_user:
            flash("Deze gebruikersnaam of dit e-mailadres bestaat al.", "error")
            return render_template('registerpage.html', name=name, email=email)

        query = "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)"
        execute_query(query, [name, email, password, "user"])

        flash("Account aangemaakt. Je kunt nu inloggen.", "success")
        return redirect(url_for('projects.login'))

    return render_template('registerpage.html', name='', email='')


@bp.route('/account', methods=['GET', 'POST'])
def account():
    """
    Laat de ingelogde gebruiker zijn wachtwoord wijzigen of account verwijderen.
    """
    user_id = session.get('user_id')
    query = "SELECT * FROM users WHERE user_id = ? LIMIT 1"
    result = execute_query(query, [user_id])

    if not isinstance(result, list) or not result:
        session.clear()
        flash("Je account is niet gevonden.", "error")
        return redirect(url_for('projects.login'))

    user = result[0]

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')

            if not current_password or not new_password:
                flash("Vul je huidige en nieuwe wachtwoord in.", "error")
                return render_template('accountpage.html', user=user)

            if user['password_hash'] != current_password:
                flash("Je huidige wachtwoord klopt niet.", "error")
                return render_template('accountpage.html', user=user)

            query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
            execute_query(query, [new_password, user_id])
            flash("Je wachtwoord is gewijzigd.", "success")
            return redirect(url_for('projects.account'))

        if action == 'delete_account':
            check_query = "SELECT COUNT(*) as count FROM testflow WHERE user_id = ?"
            check_result = execute_query(check_query, [user_id])

            if isinstance(check_result, list) and check_result and check_result[0].get('count', 0) > 0:
                flash("Je account kan niet worden verwijderd omdat er nog projecten aan gekoppeld zijn.", "error")
                return render_template('accountpage.html', user=user)

            delete_query = "DELETE FROM users WHERE user_id = ?"
            delete_result = execute_query(delete_query, [user_id])

            if isinstance(delete_result, dict) and (delete_result.get("error") or delete_result.get("reason")):
                flash("Je account kon niet worden verwijderd. Probeer het opnieuw.", "error")
                return render_template('accountpage.html', user=user)

            session.clear()
            flash("Je account is verwijderd.", "success")
            return redirect(url_for('projects.login'))

    return render_template('accountpage.html', user=user)


@bp.route('/logout')
def logout():
    """
    Log gebruiker uit.
    """

    session.clear()

    flash("Je bent uitgelogd.", "success")

    return redirect(url_for('projects.login'))
