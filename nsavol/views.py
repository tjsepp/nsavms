from django.shortcuts import render
from django.views.generic import FormView, TemplateView, RedirectView


class DashboardView(TemplateView):
    template_name = 'base.html'