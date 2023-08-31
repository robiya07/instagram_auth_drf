import random
from templated_mail.mail import BaseEmailMessage
from auth_system.services.cache_functions import setKey


class EmailActivation(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activation_code'] = random.randint(100000, 999999)

        setKey(
            key=context.get('user').phone_or_email,
            value=context.get('activation_code'),
            timeout=None
        )
        return context


def phone_activation(key):
    activation_code = random.randint(100000, 999999)
    setKey(
        key=key,
        value=activation_code,
        timeout=None
    )
    print("Your activation code:", activation_code)