
def detect_user(user):
    print(user.user_type)
    if user.user_type == 2:
        redirect_url = 'cus_dashboard'
        return redirect_url
    elif user.user_type == 1:
        redirect_url = 'staff_dashboard'
        return redirect_url
    elif user.user_type is None and user.is_superadmin:
        redirect_url = '/admin'
        return redirect_url
