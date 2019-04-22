from flask import Blueprint
from flask import request, redirect


admin_blueprint=Blueprint("admin", __name__, url_prefix="/admin")

from .views import *


@admin_blueprint.before_request
def Check_Admin():
    is_admin=session.get('is_admin', False)
    if not is_admin and request.url.endswith("admin/login")==False:
        return redirect("/")