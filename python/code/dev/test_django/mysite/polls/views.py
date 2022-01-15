from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from numpy import product
import pandas as pd

class IndexView(TemplateView):
    template_name = "index.html"
    
    def get_context_data(self):
        ctxt = super().get_context_data()
        ctxt["username"] = "太郎"
        return ctxt
    

class AboutView(TemplateView):
    template_name = "about.html"
    
    def get_context_data(self):
        ctxt = super().get_context_data()
        ctxt["skills"] = [
            "Python",
            "C++",
            "Javascript",
            "Rust",
            "Ruby",
            "PHP"
        ]
        ctxt["num_services"] = 1234567
        return ctxt
    
class DfView(TemplateView):
    template_name = "df.html"

    def get_context_data(self):
        ctxt = super().get_context_data()
        ctxt["skills"] = [
            "Pythonaaaaaaa",
            "C++",
            "Javascript",
            "Rust",
            "Ruby",
            "PHP"
        ]
        ctxt["num_services"] = 1234567
        return ctxt


    def render(request):
        product_df = pd.DataFrame(
            data={'ticker': ['PFE','MSFT','AAPL','SOXL']}
            ) #仮で作成
        context = {
            'products' : product_df.to_html(), 
            }
        return render(request, "df.html", context)
