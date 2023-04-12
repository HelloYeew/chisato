from django import forms

from collection.models import Collection


class CollectionForm(forms.ModelForm):
    name = forms.CharField(
        label='Collection Name',
        required=True,
        help_text='Name of the collection',
        max_length=100
    )
    description = forms.CharField(
        label='Collection Description',
        required=False,
        help_text='Description of the collection'
    )
    private = forms.BooleanField(
        label='Private',
        help_text='If checked, this collection will be private and can only be accessed by you.',
        required=False
    )

    class Meta:
        model = Collection
        fields = ('name', 'description', 'private')
