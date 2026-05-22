from django.forms import widgets

class CoverSelectWidget(widgets.RadioSelect):
    """
    Widget de selección de portada con miniaturas.
    No guarda estado interno — lee el queryset directamente desde self.choices
    en el momento del render, igual que hace Django con cualquier ModelChoiceField.
    """
    template_name = 'portfolio/widgets/cover_select.html'
    option_template_name = 'portfolio/widgets/cover_select_option.html'

    def optgroups(self, name, value, attrs=None):
        # ModelChoiceIteratorValue (Django 3.1+) has no .instance attribute, so we
        # build the pk→object map by iterating the underlying queryset directly.
        # This also avoids a second DB hit: ModelChoiceIterator uses queryset.iterator()
        # which bypasses _result_cache, meaning self.choices would otherwise be
        # evaluated twice (once here, once inside super().optgroups).
        media_map = {}
        qs = getattr(self.choices, 'queryset', None)
        if qs is not None:
            for obj in qs:
                media_map[str(obj.pk)] = obj

        groups = super().optgroups(name, value, attrs)

        for _group_name, subgroup, _index in groups:
            for option in subgroup:
                raw_val = str(option.get('value', ''))
                media_obj = media_map.get(raw_val)

                if media_obj:
                    try:
                        if media_obj.thumbnail:
                            option['thumb_url'] = media_obj.thumbnail.url
                            option['thumb_type'] = media_obj.type
                        elif media_obj.type == 'image' and media_obj.image_file:
                            option['thumb_url'] = media_obj.image_file.url
                            option['thumb_type'] = 'image'
                        elif media_obj.type == 'video' and media_obj.video_file:
                            option['thumb_url'] = media_obj.video_file.url
                            option['thumb_type'] = 'video'
                        else:
                            option['thumb_url'] = None
                            option['thumb_type'] = None
                    except Exception:
                        option['thumb_url'] = None
                        option['thumb_type'] = None
                else:
                    option['thumb_url'] = None
                    option['thumb_type'] = None

        return groups