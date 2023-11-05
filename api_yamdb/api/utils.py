from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from reviews.models import User


def send_confirmation_code(request):
    """
    Функция отправки пользователю кода подтверждения на электронную почту.
    """
    user = get_object_or_404(
        User,
        username=request.data.get('username'),
    )
    user.confirmation_code = default_token_generator.make_token(user)
    user.save()
    send_mail(
        subject='YaMDb registration',
        message=f'Ваш код подтверждения: {user.confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )
