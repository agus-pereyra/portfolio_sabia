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
        # Construimos el mapa pk→objeto desde self.choices, que sí está actualizado
        # porque Django lo sincroniza con el queryset del field antes de renderizar.
        media_map = {}
        for choice_value, _choice_label in self.choices:
            # choice_value puede ser '' (opción vacía) o un ModelChoiceIteratorValue
            raw = str(choice_value)
            if not raw:
                continue
            # self.choices es un ModelChoiceIterator — cada value tiene .instance
            if hasattr(choice_value, 'instance'):
                media_map[raw] = choice_value.instance

        groups = super().optgroups(name, value, attrs)

        for _group_name, subgroup, _index in groups:
            for option in subgroup:
                raw_val = str(option.get('value', ''))
                media_obj = media_map.get(raw_val)
                
                if media_obj:
                    # 1. Prioridad absoluta: Si hay miniatura (sea foto o video), usamos eso
                    if media_obj.thumbnail:
                        option['thumb_url'] = media_obj.thumbnail.url
                        option['thumb_type'] = media_obj.type
                    
                    # 2. Fallback de seguridad para imágenes viejas sin miniatura
                    elif media_obj.type == 'image' and media_obj.image_file:
                        option['thumb_url'] = media_obj.image_file.url
                        option['thumb_type'] = 'image'
                        
                    # 3. Fallback para videos rotos/sin procesar
                    elif media_obj.type == 'video' and media_obj.video_file:
                        # Dejamos la URL del video original (se mostrará vacío pero no tirará error fatal)
                        option['thumb_url'] = media_obj.video_file.url 
                        option['thumb_type'] = 'video'
                        
                    else:
                        option['thumb_url'] = None
                        option['thumb_type'] = None
                else:
                    option['thumb_url'] = None
                    option['thumb_type'] = None

        return groups