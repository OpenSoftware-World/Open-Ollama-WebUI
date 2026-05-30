from flask import Flask, request, render_template
from difflib import SequenceMatcher
from ollama_model import *
from Lang.lang import *

user = configparser.ConfigParser()
user.read('UserDatabase/user.ini')

app = Flask(__name__)

check = 0

def password_recovery_func(username, password, threshold=0.7):
    user_password = user[username]["password"]
    ratio = SequenceMatcher(None, user_password, password).ratio()
    if ratio >= threshold:
        password = user[username]["password"]
        return f"{your_password}: {password}"
    else:
        return f"{password_recovery_failed}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        lang = request.form['lang']
        set_lang(lang)
    else:
        lang = user_lang
    global check
    check = 0
    return render_template("index.html", app_title=app_title, lang=lang, user_name_input=user_name_input, password_input=password_input, login_var=login_var, new_user_register=new_user_register)

@app.route('/login', methods=['POST'])
def login():
    global check
    username = request.form['username']
    password = request.form['password']

    if username in user and user[username]["password"] == password:
        check = 1
        return render_template("login_successfully.html", login_successfully=login_successfully, welcome=welcome, username=username, go_to_app=go_to_app)
    else:
        username = request.form['username']
        return render_template("login_failed.html", login_failed=login_failed, login_failed_description=login_failed_description, username=username, user_register=user_register, try_again=try_again, password_forget=password_forget)

@app.route('/passrecovery', methods=['GET', 'POST'])
def pass_recovery():
    if request.method == 'POST':
        username = request.form['username']
        return render_template("passrecovery.html", password_recovery=password_recovery, username=username, password_recovery_=password_recovery_, password_recovery_input=password_recovery_input, pass_rec_=pass_rec_, password_recovery_submit=password_recovery_submit)
    
@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_pass_recovery = password_recovery_func(username, password)
        return render_template("recovery.html", password_recovery_report=password_recovery_report, username=username, user_pass_recovery=user_pass_recovery, try_again=try_again)

@app.route('/user')
def user_form():
    if request.method == 'POST':
        username = request.form['username']

        if username in user:
            return render_template("user_register_failed.html", user_register_failed=user_register_failed, try_again=try_again)

    return render_template("user_register.html", new_user_register=new_user_register, user_name_input=user_name_input, password_input=password_input, register=register)

@app.route('/adduser', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    if user.has_section(f"{username}"):
        return render_template("user_name_failed.html", user_register_failed_title=user_register_failed_title, user_register_failed=user_register_failed, try_again=try_again)
    for section in user.sections():
        if user[section]["ip_address"] == ip_address:
            return render_template("user_ip_failed.html", user_register_failed_title=user_register_failed_title, user_register_ip=user_register_ip, try_again=try_again)
    else:
        if password == "":
            return render_template("user_password_failed.html", user_register_failed_title=user_register_failed_title, user_register_failed_description=user_register_failed_description, try_again=try_again)
    user_ip = request.remote_addr
    user.add_section(f"{username}")
    user.set(f"{username}", "password", f"{password}")
    user.set(f"{username}", "ip_address", f"{user_ip}")
    with open("UserDatabase/user.ini", "w") as configfile:
        user.write(configfile)
        return render_template("user_register_success.html", user_register_successfully=user_register_successfully, user_register_successfully_description=user_register_successfully_description, login_var=login_var)

@app.route('/app', methods=['GET', 'POST'])
def app_page():
    if check == 1:
        return render_template("ollama_webui.html", ollama_web_ui_title=ollama_web_ui_title, user_model=user_model, model_question=model_question, model_submit=model_submit, exit=exit)
    else:
        return render_template("app_requirements.html", app_requirements=app_requirements, app_requirements_description=app_requirements_description, login_var=login_var)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == "POST":
        model = request.form["model"]
        msg = request.form["msg"]
        user_response = f"{user_}: {msg}"
        model_response = load_model(model, msg)
        return render_template("ollama_webui_chat.html", model=model, user_response=user_response, model_response=model_response, model_question=model_question, model_submit=model_submit, exit=exit)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)