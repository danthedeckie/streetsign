post_types = {
{%- for t in types %}
"{{ t[0] }}" : {{ t[1]|trim -}} {{- ',' if not loop.last -}}
{% endfor %}
}
