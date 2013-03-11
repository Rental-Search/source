from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def proapp_dashboard(request):
	return render(request, 'proapp/app.html', {})