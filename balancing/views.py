# Dynamic Balance
# Toth, Ighor <toth@ighor.com> - https://github.com/igtoth/dynamicbalance

from balancing.models import Tickers
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from matplotlib import pylab
from pylab import *
import simplejson as json
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
import pandas as pd
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

from .forms import BalancingForm, PlotForm
from .charts import simple

# Create your views here.

def balancing_view(request):
    import base64
    import random
    import datetime
    import django
    import PIL, PIL.Image
    import io
    from matplotlib.backends.backend_agg import FigureCanvasAgg 
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import numpy as np
    import balancing.pydynamicbalance as pyd

    def full_frame(width=None, height=None):
        import matplotlib as mpl
        mpl.rcParams['savefig.pad_inches'] = 0
        figsize = None if width is None else (width, height)
        fig = pylab.figure(figsize=figsize)
        ax = pylab.axes([0,0,1,1], frameon=False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        pylab.autoscale(tight=True)

    form = BalancingForm(request.POST or None, initial={
                                                'prop_r_fix': 50,
                                                'prop_r_var': 50,
                                                'param_alfa': 40,
                                                'param_h': 100,
                                                'ativo' : 'USIM5' ,
                                                'periodo_ini' : '01-01-2013',
                                                'periodo_fim': '15-10-2019',
                                                'pat_ini': 100000,
                                                })

    if form.is_valid():
        print(form.cleaned_data)
        form = BalancingForm()

    if request.POST.get('pat_ini') != None:
        VALOR_A_INVESTIR = int(request.POST.get('pat_ini'))
    else: 
        VALOR_A_INVESTIR = int('100000')
    
    if request.POST.get('prop_r_fix') != None:
        DECIMAL_PERCENTUAL_RENDA_FIXA = request.POST.get('prop_r_fix')
        DECIMAL_PERCENTUAL_RENDA_FIXA = int(DECIMAL_PERCENTUAL_RENDA_FIXA)/100
    else:
        DECIMAL_PERCENTUAL_RENDA_FIXA = 0.5

    if request.POST.get('prop_r_var') != None:
        DECIMAL_PERCENTUAL_RENDA_VARIAVEL = request.POST.get('prop_r_var')
        DECIMAL_PERCENTUAL_RENDA_VARIAVEL = int(DECIMAL_PERCENTUAL_RENDA_VARIAVEL)/100
    else:
        DECIMAL_PERCENTUAL_RENDA_VARIAVEL = 0.5

    if request.POST.get('periodo_ini') != None:
        PERIODO_INI = datetime.datetime.strptime(request.POST.get('periodo_ini'), '%d-%m-%Y').strftime('%Y%m%d')
    else:
        PERIODO_INI = '20130101'

    if request.POST.get('periodo_fim') != None:
        PERIODO_FIM = datetime.datetime.strptime(request.POST.get('periodo_fim'), '%d-%m-%Y').strftime('%Y%m%d')
    else:
        PERIODO_FIM = '20191010'

    if request.POST.get('param_alfa') != None:
        ALPHA = request.POST.get('param_alfa')
        ALPHA = int(ALPHA)/100
    else:
        ALPHA = 0.4

    if request.POST.get('param_h') != None:
        H = request.POST.get('param_h')
        H = int(H)/100
    else:
        H = 1

    if request.POST.get('ativo') != None:
        TICKER = request.POST.get('ativo')
        TICKER = TICKER.upper()
    else:
        TICKER = 'USIM5'


    port = pyd.Portifolio(VALOR_A_INVESTIR, DECIMAL_PERCENTUAL_RENDA_FIXA, DECIMAL_PERCENTUAL_RENDA_VARIAVEL)
    df, statistics_data = port.run_simulation(PERIODO_INI,PERIODO_FIM,ALPHA,H,TICKER)

    df['Date'] =  pd.to_datetime(df['Date'], format='%Y-%m-%d')
    buf = io.BytesIO()

    fig, ax = plt.subplots(figsize=(15,7))
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    full_frame()
    df.plot(linestyle='-', x='Date', y='stock_Portifolio_value', color='#8DD1D3', ax=ax)
    df.plot(linestyle='-', x='Date', y='lft_Portifolio_value', color='#B69EAD', ax=ax)
    df.plot(linestyle='-', x='Date', y='Total', color='#BFBFBF', ax=ax)
    df.plot(linestyle='-', x='Date', y='TotalBalanced', color='#FBD079', ax=ax)

    font = font_manager.FontProperties(family='Arial', style='normal', size=9)
    ax.grid(axis='y',linestyle='--')
    ax.legend(['ATIVO','LFT','s/ Balanceamento','c/ Balanceamento'],prop=font)
    pylab.tick_params(axis='x', labelsize=9)
    pylab.tick_params(axis='y', labelsize=9)
    ax.set_title(TICKER, fontsize=15) 
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')

    response['Content-Length'] = str(len(response.content))
    
    def real_br_money_mask(my_value):
        a = '{:,.2f}'.format(float(my_value))
        b = a.replace(',','v')
        c = b.replace('.',',')
        return c.replace('v','.')

    stats = {}
    for key,val in statistics_data.items():
        value = np.round(val,2)
        if key == "total_result" or key == "total_bal_result" or key == "stock_earnings" or key == "lft_earnings":
            value = value*100
        if key == "max_bal_result" or key == "min_bal_result":
            value = real_br_money_mask(value)
        stats.update({key:value})

    encoded = base64.b64encode(buf.getvalue()).decode('ascii')
    #buf.seek(0)
    #img_base64 = bytes("data:image/png;base64,", encoding='utf-8') + encoded

    context = {
        "title": "Dashboard",
        "form": form,
        "statistics": stats,
        "image": encoded,
    }
    return render(request, "dashboard.html", context)



def plot2(request,post=None):
    #form = PlotForm(request.GET or None)
    #if form.is_valid:
    #    print(form.cleaned_data)
    #    form = PostForm()

    import random
    import datetime
    import django
    #import pylab 
    import PIL, PIL.Image
    import io
    #import pyoplabmd as op
    import balancing.pydynamicbalance as pyd

    from matplotlib.backends.backend_agg import FigureCanvasAgg 
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

    VALOR_A_INVESTIR = int(request.GET.get('pat_ini'))
    DECIMAL_PERCENTUAL_RENDA_FIXA = request.GET.get('prop_r_fix')
    DECIMAL_PERCENTUAL_RENDA_FIXA = int(DECIMAL_PERCENTUAL_RENDA_FIXA)/100
    DECIMAL_PERCENTUAL_RENDA_VARIAVEL = request.GET.get('prop_r_var')
    DECIMAL_PERCENTUAL_RENDA_VARIAVEL = int(DECIMAL_PERCENTUAL_RENDA_VARIAVEL)/100
    #PERIODO_INI = request.GET.get('periodo_ini')
    PERIODO_INI = datetime.datetime.strptime(request.GET.get('periodo_ini'), '%d-%m-%Y').strftime('%Y%m%d')
    #PERIODO_FIM = request.GET.get('periodo_fim')
    PERIODO_FIM = datetime.datetime.strptime(request.GET.get('periodo_fim'), '%d-%m-%Y').strftime('%Y%m%d')
    ALPHA = request.GET.get('param_alfa')
    ALPHA = int(ALPHA)/100
    H = request.GET.get('param_h')
    H = int(H)/100
    TICKER = request.GET.get('ativo')
    TICKER = TICKER.upper()
    #
    port = pyd.Portifolio(VALOR_A_INVESTIR, DECIMAL_PERCENTUAL_RENDA_FIXA, DECIMAL_PERCENTUAL_RENDA_VARIAVEL)
    df, statitistics = port.run_simulation(PERIODO_INI,PERIODO_FIM,ALPHA,H,TICKER)
    #port= pyd.Portifolio(100000,0.5,0.5)
    #df, statitistics = port.run_simulation('20140101','20191015',0.15,1,'USIM5')

    df['Date'] =  pd.to_datetime(df['Date'], format='%Y-%m-%d')
    buf = io.BytesIO()



    def full_frame(width=None, height=None):
        import matplotlib as mpl
        mpl.rcParams['savefig.pad_inches'] = 0
        figsize = None if width is None else (width, height)
        fig = pylab.figure(figsize=figsize)
        ax = pylab.axes([0,0,1,1], frameon=False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        pylab.autoscale(tight=True)

    #canvas = FigureCanvasAgg(fig)
    fig, ax = plt.subplots(figsize=(15,7))
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    #df.plot_date(ax)
    #ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    #ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    #ax.xticks(rotation=30)
    full_frame()   
    df.plot(linestyle='-', x='Date', y='stock_Portifolio_value', color='#8DD1D3', ax=ax)
    df.plot(linestyle='-', x='Date', y='lft_Portifolio_value', color='#B69EAD', ax=ax)
    df.plot(linestyle='-', x='Date', y='Total', color='#BFBFBF', ax=ax)
    df.plot(linestyle='-', x='Date', y='TotalBalanced', color='#FBD079', ax=ax)
    font = font_manager.FontProperties(family='Arial',
                                   style='normal', size=9)
    ax.grid(axis='y',linestyle='--')
    ax.legend(['ATIVO','LFT','s/ Balanceamento','c/ Balanceamento'],prop=font)
    pylab.tick_params(axis='x', labelsize=9)
    pylab.tick_params(axis='y', labelsize=9)
    #ax.set_xticklabels(formatter,rotation=90)
    ax.set_title(TICKER, fontsize=15) 
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    #fig.clear()
    #df.clear()
    response['Content-Length'] = str(len(response.content))
    return response
    #canvas = FigureCanvas(fig)
    #graphic1  =django.http.HttpResponse(content_type='image/png')
    #graphic1 = HttpResponse(content_type='image/jpg')
    #canvas.print_png(graphic1)
    #return render(request, 'text.html',{'graphic':graphic1}) 



def my_plot(request):
    import subprocess
    plot = subprocess.check_output(['gnuplot', '-e', 'set terminal pngcairo; plot sin(x)'])
    response = HttpResponse(plot, content_type="image/png")
    return response

def ticker_name_search(request):
    if request.is_ajax():
        q = request.GET.get('term','')
        names = Tickers.objects.filter(label__istartswith=q)
        result = []
        for n in names:
            name_json = n.name
            label_json = n.label
            result.append(label_json)
            data = json.dumps(result)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
