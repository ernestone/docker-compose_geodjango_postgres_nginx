from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy

from .forms import UserSampleChangeForm, UserSampleCreationForm

from sample_admin_app.models import UserSample


class UserSampleAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserSampleChangeForm
    add_form = UserSampleCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Relations', {'fields': ('countries',)}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',)}),
        # ('Important dates', {'fields': ('last_login', 'date_joined')})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'countries'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Subclaseo para enviar mail de reset password al crear un nuevo usuario

        Args:
            request:
            obj:
            post_url_continue:

        Returns:

        """
        send_mail_reset_password_for_user(obj, request)

        return super(UserSampleAdmin, self).response_add(request, obj, post_url_continue)


admin.site.site_title = ugettext_lazy('Sample Admin')
admin.site.site_header = ugettext_lazy('Admin Sample')
admin.site.index_title = ugettext_lazy('Admin')

admin.site.register(UserSample, UserSampleAdmin)
# Se quita la gestion de GRUPOS por no ser necesaria
admin.site.unregister(Group)


def send_mail_reset_password_for_user(user, request,
                                      subject_template_name='new_user_email_subject.txt',
                                      email_template_name='new_user_email.html',
                                      from_email=None, use_https=False, **extra_email_context):
    """
    Envia mail reset_password para usuario creado

    Args:
        user:
        subject_template_name:
        email_template_name:
        from_email:
        request:
        use_https:
        **extra_email_context:

    Returns:

    """
    email_field_name = user.get_email_field_name()
    email = getattr(user, email_field_name)
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    context = {
        'email': email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
        **extra_email_context
    }

    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [email])

    email_message.send()
