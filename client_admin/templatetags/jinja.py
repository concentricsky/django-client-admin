import re
import jingo
from django import template

register = template.Library()

def block_super():
    return '{{super()}}'
register.simple_tag(block_super)

@register.tag(name="extends_jinja")
def do_extends_jinja(parser, token):
    #import pdb; pdb.set_trace()
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    nodelist = parser.parse()

    return JinjaNode(format_string[1:-1], nodelist)

class JinjaNode(template.Node):
    def __init__(self, template, nodelist):
        self.parent_template = template
        self.nodelist = nodelist
    def render(self, context):
        output_string = '{%% extends "%s" %%}' % self.parent_template
        for node in self.nodelist:
            if node.__class__.__name__ == 'BlockNode':
                # replace dashes in block names because they aren't allowed in jinja2
                node_name = node.name.replace('-','_')

                # handle {{super()}} specially, as that needs to be passed through from django templates to jinja renderer
                rendered_node = node.render(context)
                r = re.compile(r'\{\{\s*super\(\)\s*\}\}')
                if re.search(r, rendered_node):
                    spr = '{{super()}}'
                    rendered_node = re.sub(r, '', rendered_node)
                else:
                    spr = ''
                # wrap blocks in a {{ raw }} tag in case we need to display tags in admin pages (eg. emailtemplates)
                output_string += '{%% block %s %%}%s{%% raw %%} %s {%% endraw %%}{%% endblock %%}' % (node_name, spr, rendered_node)
            else:
                output_string += node.render(context)
        output_template = jingo.env.from_string(output_string)
        output_template.name = self.parent_template
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        return jingo.render_to_string(context['request'], output_template, context_dict)