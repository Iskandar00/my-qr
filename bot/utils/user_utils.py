from asgiref.sync import sync_to_async

from v1.models import CustomUser


@sync_to_async
def get_by_phone_user(phone_number):
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        return user
    except CustomUser.DoesNotExist:
        print("user phone not found!")
        return None

@sync_to_async
def save_user(user):
    user.save()
