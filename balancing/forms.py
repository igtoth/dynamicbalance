from django import forms

PERCENTAGES = list(range(1, 101))

class BalancingForm(forms.Form):
    prop_r_fix = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=((str(x), str(x)+'%') for x in range(1,101)), required='true', label='Renda Fixa')
    #prop_r_fix = forms.CharField()
    prop_r_var = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=((str(x), str(x)+'%') for x in range(1,101)), required='true', label='Renda Variável')
    periodo_ini = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker form-control','data-date-format':'dd-mm-yyyy','readonly':'true','size':10}), label='Início')
    periodo_fim = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker form-control','data-date-format':'dd-mm-yyyy','readonly':'true','size':10}), label='Fim')
    ativo = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Ativo')
    pat_ini = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Patrimônio Inicial')
    param_h = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=((str(x), str(x)+'%') for x in range(1,101)), required='true', label='Parâm. H')
    param_alfa = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=((str(x), str(x)+'%') for x in range(1,101)), required='true', label='Parâm. Alfa')

class AutoCompleteForm(forms.Form):
    ativo = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Ativo')


class PlotForm(forms.Form):
    x = forms.CharField()
    y = forms.CharField()
