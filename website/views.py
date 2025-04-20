from flask import Blueprint, render_template, redirect, url_for
from . import pictures

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", pictures = pictures)

@views.route('/page/<int:page_id>')
def page(page_id):
    if page_id == int:
        return redirect(url_for('views.home'))
    return redirect(url_for('views.home'))
    