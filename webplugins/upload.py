from flask import Blueprint, render_template, request, redirect, url_for, send_file, abort
from main import isAllowed
import os

class CWWPUpload():
    blueprint = Blueprint('CWWPUpload', __name__, template_folder="./")
    name = "HTTP Upload Server"
    mainpage = "/uploads"
    description = """
Opens the 'lootbox' - the uploaded files of clients
"""
    customButtons = None

    @blueprint.route('/uploads/<path:req_path>')
    def uploadDir(req_path):
        if not isAllowed(request): return redirect(url_for('login'), code=302)
        BASE_DIR = './uploads/'

        # Joining the base and the requested path
        abs_path = os.path.join(BASE_DIR, req_path.replace("/..", "")) # to prevent path traversals

        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            return send_file(abs_path)
        
        files = os.listdir(abs_path)
        return render_template('files.html', files=files)
    
    @blueprint.route('/uploads/')
    def uploadDirIndex():
        if not isAllowed(request): return redirect(url_for('login'), code=302)
        BASE_DIR = './uploads/'

        # Joining the base and the requested path
        abs_path = os.path.join(BASE_DIR) # to prevent path traversals

        files = os.listdir(abs_path)
        return render_template('files.html', files=files)