from flask import  jsonify, request, Blueprint, redirect, url_for
from auth.decoraters import auth_required, error_handler
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import re
import logging
import sys


from shared import invite

users_blueprint = Blueprint("users", __name__, template_folder=None, static_folder=None)

emails = set()

@users_blueprint.route("/", methods=["GET"])
def users_index():
    return jsonify({"message": "users api"}), 200


@users_blueprint.route("/invite", methods=["POST", "GET" ])
@error_handler
def invite_users():
    if request.args.get("instructions")!= "refresh" and request.method == "GET":
        # add_emails_and_send_invitations()
        invite.add_emails_and_send_invitations()
        return jsonify({"message": "Invitations sent successfully"}), 200
    else:
        email = request.args.get("email")
        pattern = r'^[a-zA-Z0-9._%+-]+@asu\.edu$'
        if email is None:
            return jsonify({"error": "Missing email parameter"}), 202
        elif re.match(pattern, email):
            emails.add(email)
            if len(emails) > 10:
                if invite.login():
                    invite.add_emails_and_send_invitations()
                    invite.emails.clear()
                    return jsonify({"message": "Invitations sent successfully"}), 200
                else:
                    invite.emails.add(email)
                    return jsonify({"message": "Logged Out"}), 200
            else:
                return jsonify({"message": "Email added to the list"}), 200
    

    
@users_blueprint.route("/login", methods=["POST"])
@auth_required
def login_route():
    if invite.login():
         return redirect(url_for('users_blueprint.invite_users', instructions="refresh"))

