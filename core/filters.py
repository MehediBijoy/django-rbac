from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    ordering_reference_fields = []
    ordering_param = 'sort_by'
    ordering_symbol_param = 'sort_order'
    ordering_lookups_map = {}

    def get_ordering(self, request, queryset, view):
        sort_by = request.query_params.get(self.ordering_param)
        if sort_by:
            fields = [
                self.get_odering_symbol_format(request, param.strip())
                for param in sort_by.split(',')
            ]
            ordering = self.map_fields_with_lookups(
                queryset, fields, view, request
            )
            if ordering:
                return ordering

        return self.get_default_ordering(view)

    def get_default_fields_lookups(self, queryset, view, context={}) -> dict[str, tuple]:
        serializer_class = getattr(view, 'serializer_class', None)
        model_class = queryset.model
        model_property_names = [
            attr for attr in dir(model_class)
            if isinstance(getattr(model_class, attr), property) and attr != 'pk'
        ]

        ordering_lookups = dict()
        for field_name, field in serializer_class(context=context).fields.items():
            if (
                not getattr(field, 'write_only', False) and
                not field.source == '*' and
                field.source not in model_property_names
            ):
                ordering_lookups[field_name] = self.extract_source_key(
                    field.source.replace('.', '__') or field_name
                )
        ordering_lookups.update(self.ordering_lookups_map)
        return ordering_lookups

    def map_fields_with_lookups(self, queryset, fields: list[str], view, request):
        lookups = self.get_default_fields_lookups(
            queryset, view, {'request': request}
        )

        def trans_keys(key: str):
            prefix = '-' if key.startswith('-') else ''
            return prefix + lookups[key.lstrip('-')]

        return [
            trans_keys(field) for field in fields
            if field.lstrip('-') in lookups
        ]

    def extract_source_key(self, value: str):
        if value.startswith('get_') and value.endswith('_display'):
            return value.removeprefix('get_').removesuffix('_display')
        return value

    def get_odering_symbol_format(self, request, value: str):
        sort_order: str = request.query_params.get(
            self.ordering_symbol_param, 'asc'
        )

        value = value.lstrip('-')
        if sort_order.lower() == 'desc':
            return f'-{value}'

        return value


class SearchFilter(filters.SearchFilter):
    search_param = 'search'
