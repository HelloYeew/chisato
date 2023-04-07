from django.forms import forms


class BackupFileUploadForm(forms.Form):
    osu_file = forms.FileField(
        label='osu! Database Backup File',
        required=True,
        help_text='osu!.db file from your osu! folder. (Must be osu!.db)'
    )
    collection_file = forms.FileField(
        label='Collection Database Backup File',
        required=True,
        help_text='collection.db file from your osu! folder (Must be collection.db)'
    )

    class Meta:
        fields = ['osu_file', 'collection_file']

    def clean(self):
        cleaned_data = super().clean()
        osu_file = cleaned_data.get('osu_file')
        collection_file = cleaned_data.get('collection_file')
        # Check file name must be osu!.db and collection.db
        if osu_file.name != 'osu!.db':
            self.add_error('osu_file', 'File name must be osu!.db')
        if collection_file.name != 'collection.db':
            self.add_error('collection_file', 'File name must be collection.db')
