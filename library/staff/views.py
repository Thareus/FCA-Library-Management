from django.views import View
from django.shortcuts import redirect
from .models import BookInstance

class ChangeRentalStatusView(View):
    def get(self, request, book_instance_id):
        pass

    def post(self, request, book_instance_id):
        pass

