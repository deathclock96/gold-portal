import os
import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext
from sys import argv

def get_db():
    if 'db' not in g:
        # open a connection, save it to close when done
        DB_URL = os.environ.get('DATABASE_URL', None)
        if DB_URL:
            g.db = psycopg2.connect(DB_URL, sslmode='require')
        else:
            g.db = psycopg2.connect(
                f"dbname={current_app.config['DB_NAME']}" +
                f" user={current_app.config['DB_USER']}"
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() # close the connection


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        cur = db.cursor()
        cur.execute(f.read())
        cur.close()
        db.commit()

def create_user():
    con = get_db()
    print("Enter user's email")
    email = input(">")
    print("Enter user's password")
    password = input(">")
    print("Enter user's role")
    role = input(">")
    with current_app.open_resource('schema.sql') as f:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(email, password, role) VALUES (%s, %s, %s)",
            (email, password, role)
        )
        con.commit()
        cur.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('create-user')
@with_appcontext
def create_user_command():
    create_user()
    click.echo('Created user')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
