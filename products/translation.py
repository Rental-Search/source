from modeltranslation.translator import register, TranslationOptions
from products.models import Category


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
	fields = ('name', 'slug', 'title', 'description', 'header', 'footer', 'image',)