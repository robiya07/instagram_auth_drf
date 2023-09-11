import random
from templated_mail.mail import BaseEmailMessage
from auth_system.services.cache_functions import setKey


class EmailActivation(BaseEmailMessage):
    template_name = "email/activation.html"

    def __init__(self, request, context, activation_code):
        self.activation_code = activation_code
        super().__init__(request=request, context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activation_code'] = self.activation_code
        return context


def phone_activation(phone, code):
    print("Your phone:", phone)
    print("Your activation code:", code)
