
from secrets import choice
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse

from loguru import logger

class DefaultViewMixin:
    template_name = None

    def get(self, request):
        return render(request=self.request, template_name=self.template_name)


class SendFormMixin:
    form = None
    template_name = None
    reverse_name = "index_url"

    def get(self, request):
        return render(request=request, template_name=self.template_name, context={"form": self.form()})
    
    def post(self, request):
        f = self.form(request.POST)
        if f.is_valid() and f.isValid() and request.user.is_authenticated == False:
            try:
                f.save()
                pass
            except: pass
            logger.success("Success")
            return redirect(self.reverse_name)
        else:
            logger.error("Success denied")
            return render(request=self.request, template_name=self.template_name, context={"form": self.form()})
