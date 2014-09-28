from django.forms import ModelForm
from contest.models import Gamer


class GamerForm(ModelForm):
	class Meta:
		model = Gamer
		fields = ['like_facebook',]


