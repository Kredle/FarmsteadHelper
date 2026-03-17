import re
from django.http import JsonResponse
import requests
from django.http import HttpResponseForbidden # For denying access
from farmstead_farmer import settings

# Шляхи, які дозволені для доступу
ALLOWED_PATHS = [
    # Animals branch paths
    "/catalog/animals/",
    r"/catalog/animals/\d+/",  # Path with animal_id parametr
    r"/catalog/animals/\d+/\d+/", # Path with sort_id parametr

    # Calendar paths
    "/api/get_sorts/",
    "/calendar/",
    "/api/get_sort_detail/",

    # Catalog paths
    "/catalog/",
    "/api/search/",
    "/api/filter_catalog/",

    # Feedback paths
    "/feedback/",
    "/submit-feedback/",

    # Forum paths
    "/forum/",
    "/forum/test/",
    "/forum/create-discussion/",
    "/forum/create/",
    r"/forum/topic/\d+/",  # Path with pk parameter
    "/forum/get_topics/",
    "/forum/get_popular_topics/",
    r"/forum/update_topic/\d+/",
    r"/forum/delete_topic/\d+/",
    r"/forum/edit-topic/\d+/",
    r"/forum/edit_topic/\d+/",
    r"/forum/add_comment/\d+/",
    r"/forum/get_user_reaction/\d+/",
    r"/forum/topic/\d+/comments_list/",
    r"/forum/update_comment/\d+/",
    r"/forum/delete_comment/\d+/",
    "/forum/update-comment-reaction/",
    r"/forum/edit_comment/\d+/",
    r"/forum/get_comment/\d+/",
    "/api/toggle_favorite/",
    "/api/check_favorite/",

    # Paths from interactive_map/
    "/map/",
    "/map/interactive-map/",
    "/map/save-interactive-map/",
    "/map/check-map/",
    r"/map/get-map/\d+/",  # Path with user_id parameter
    "/map/update-interactive-map/",

    # Main page
    "/",

    # Paths from api/ and catalog/
    "/api/login/",
    "/api/register/",
    "/api/user-data/",
    "/api/logout/",
    "/api/send-otp/",
    "/api/verify-otp/",
    "/api/check-user/",
    "/api/check-user-pass/",
    "/api/reset-password/",
    "/api/profile/",
    "/api/profile/update/",
    "/api/check-auth/",
    "/api/send-otp-reset/",
    "/api/change-username/",
    "/api/change-bio/",
    "/api/change-password/",
    "/api/upload-avatar/",
    "/api/update-name/",
    "/api/delete-account/",
    "/api/send-otp-email/",
    "/api/change-email/",
    "/api/send-otp-delete/",
    "/api/toggle_favorite/",
    "/api/check_favorite/",
    "/api/check-map/",
    "/api/check_profile/",
    "/api/is_favorite_private_change/",
    "/api/is_map_private_change/",
    "/api/set_moderation/",
    "/api/verify_moderation/",
    "/api/report/",

    "/update-author-name/",
    "/register/",
    "/login/",
    "/report/",

    "/catalog/flowers/",
    r"/catalog/flowers/\d+/",  # Path with id parameter

    "/catalog/trees/",
    r"/catalog/trees/\d+/\d+/",  # Path with two parameters (tree_id, sort_id)
    r"/catalog/trees/\d+/",  # Path with tree_id parameter

    "/catalog/vegetables/",
    r"/catalog/vegetables/\d+/",  # Path with veg_id parameter
    r"/catalog/vegetables/\d+/\d+/"  # Path with two parameters (veg_id, sort_id)
]

class APIWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # CHECK IF PATH IS FROM ALLOWED_PATHS
        if any(re.match(allowed_path, path) for allowed_path in ALLOWED_PATHS):
            return self.get_response(request)

        # If path is not from ALLOWED_PATHS
        return JsonResponse({"error": "Not allowed"}, status=403)


BLOCKED_COUNTRIES = ['RU', 'BY']

iPinfo_token = settings.IPinfo_token
# Function for getting country from ip by using ipinfo.io
def get_country_from_ip(ip):
    try:
        #url = f'https://ipinfo.io/{ip}/country?token={iPinfo_token}'
        response = requests.get(url, timeout=3)

        if response.status_code == 200:
            country = response.text.strip()
            return country
    except Exception as e:
        print(f"[ERROR] Exception while fetching country for IP {ip}: {e}")
    return None


class GeoBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR') # Getting the ip
        if ip:
            ip = ip.split(',')[0].strip()
            country = get_country_from_ip(ip) # Getting the country
            print(ip)
            print(country)
            if country in BLOCKED_COUNTRIES:
                return HttpResponseForbidden("Access denied.")  # Block if country is in BLOCKED_COUNTRIES
        return self.get_response(request)

