from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    name = "portfolio"

    def ready(self):
        from django.db.models.signals import post_init
        from .models import Media

        # Django's ImageField connects update_dimension_fields to post_init so
        # that width/height are recomputed whenever they are NULL on a loaded
        # instance. On S3 storage this means a full file.open() → S3 GET per
        # row, taking ~1.5 s each at sa-east-1 latency.
        #
        # Media.save() already computes and stores width/height explicitly, so
        # the signal is redundant for every read path. Disconnecting it makes
        # queryset evaluation instant again; new uploads still get correct
        # dimensions via ImageFileDescriptor.__set__ → update_dimension_fields
        # (force=True), which is called directly (not through the signal).
        image_field = Media._meta.get_field('image_file')
        post_init.disconnect(
            receiver=image_field.update_dimension_fields,
            sender=Media,
        )
