from django.conf import settings

def authentication(password):
    """
    パスワード認証を行う
    """
    if password == settings.ADMIN_SECRET_KEY:
        return True
    else:
        return False
