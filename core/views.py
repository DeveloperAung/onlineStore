from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites import requests
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage

from core.forms import RegistrationForm
from core.models import User
from userProfile.models import UserProfile


def check_role_staff(user):
    if user.user_type == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.user_type == 2:
        return True
    else:
        raise PermissionDenied


def dashboard(request):
    return render(request, 'account/dashboard.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password)
            user.phone_number = phone_number
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Thank you for registering with us.'
                                      'We have sent you a verification email to your email address'
                                      '[youremail@gmail.com]. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print('b4_auth', username, password)

        user = auth.authenticate(username=username, password=password)
        print('aft_auth', user)
        if user is not None:
            try:
                # cart = Cart.objects.get(cart_id=_cart_id(request))
                # is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                # if is_cart_item_exists:
                #     cart_item = CartItem.objects.filter(cart=cart)
                #
                #     # Getting the product variations by cart id
                #     product_variation = []
                #     for item in cart_item:
                #         variation = item.variations.all()
                #         product_variation.append(list(variation))
                #
                #     # Get the cart items from the user to access his product variations
                #     cart_item = CartItem.objects.filter(user=user)
                #     ex_var_list = []
                #     id = []
                #     for item in cart_item:
                #         existing_variation = item.variations.all()
                #         ex_var_list.append(list(existing_variation))
                #         id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    # for pr in product_variation:
                    #     if pr in ex_var_list:
                    #         index = ex_var_list.index(pr)
                    #         item_id = id[index]
                    #         item = CartItem.objects.get(id=item_id)
                    #         item.quantity += 1
                    #         item.user = user
                    #         item.save()
                    #     else:
                    #         cart_item = CartItem.objects.filter(cart=cart)
                    #         for item in cart_item:
                    #             item.user = user
                    #             item.save()
                pass
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'account/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        # if Account.objects.filter(email=email).exists():
        #     user = Account.objects.get(email__exact=email)
        #
        #     # Reset password email
        #     current_site = get_current_site(request)
        #     mail_subject = 'Reset Your Password'
        #     message = render_to_string('accounts/reset_password_email.html', {
        #         'user': user,
        #         'domain': current_site,
        #         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        #         'token': default_token_generator.make_token(user),
        #     })
        #     to_email = email
        #     send_email = EmailMessage(mail_subject, message, to=[to_email])
        #     send_email.send()

        #     messages.success(request, 'Password reset email has been sent to your email address.')
        #     return redirect('login')
        # else:
        #     messages.error(request, 'Account does not exist!')
        #     return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')
