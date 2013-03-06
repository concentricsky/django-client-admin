from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
from django.conf import settings


def thumbnail(image_path):
   return u'<img src="%s" class="imageupload-thumbnail">' % image_path


class ThumbnailImageWidget(AdminFileWidget):
    template_with_initial = '<p class="file-upload">%(input)s%(clear_template)s</p>'
    clear_checkbox_label = "<span>Undo</span> Delete Image"

    def render(self, name, value, attrs=None):
        output = []
        if value:
            file_path = '%s%s' % (getattr(settings, 'MEDIA_URL', '/media/'), value)
            try:
                output.append('<a target="_blank" href="%s" class="imageupload-thumbcontainer">%s</a>' %
                       (file_path, thumbnail(file_path)))
            except IOError:
                output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' %
                       ('Currently:', file_path, value, 'Change:'))
        else:
            output.append(thumbnail('%sclient_admin/images/missing_image.png' % getattr(settings, 'STATIC_URL', '/static/')))

        output.append('<div class="imageupload-widget"><a href="#" class="file_upload_button">Change Image</a><p class="file-upload">%s</p></div>' % super(ThumbnailImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))