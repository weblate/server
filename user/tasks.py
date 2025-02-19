from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from neatplus.celery import no_simultaneous_execution


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
@no_simultaneous_execution
def send_user_mail(self, user_id, subject, message, from_email, **kwargs):
    get_user_model().objects.get(id=user_id).email_user(
        subject, message, from_email=from_email, **kwargs
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
@no_simultaneous_execution
def send_email_address_mail(
    self, email_address, subject, message, from_email=None, **kwargs
):
    send_mail(subject, message, from_email, [email_address])
