from django import forms


class ServerForm(forms.Form):
    status = forms.CharField(widget=forms.HiddenInput())
    instanceId = forms.CharField(widget=forms.HiddenInput())
