from django.http import HttpResponse
from django.shortcuts import render
from numpy import product
import pandas as pd

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.あああ")

def render(request):
    product_df = pd.DataFrame(
            data={'ticker': ['PFE','MSFT','AAPL','SOXL']}
            ) #仮で作成
    context = {
            'products' : product_df.to_html(), 
            }
    return render(request, "index.html", context)