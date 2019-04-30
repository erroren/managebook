from django.contrib import admin
from .models import StudentUser, Book, BorrowMessage, Hotpic, Message
# Register your models here.
admin.site.register(StudentUser)
admin.site.register(Book)
admin.site.register(BorrowMessage)
admin.site.register(Hotpic)
admin.site.register(Message)