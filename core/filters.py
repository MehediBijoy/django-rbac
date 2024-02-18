from rest_framework import filters


class DefaultFieldExtractMixin:

    def get_default_fields_lookups(self, queryset, view, context={}) -> dict[str, str]:
        serializer_class = getattr(view, 'serializer_class', None)
        model_class = queryset.model
        model_property_names = [
            attr for attr in dir(model_class)
            if isinstance(getattr(model_class, attr), property) and attr != 'pk'
        ]

        fields_lookups = dict()
        for field_name, field in serializer_class(context=context).fields.items():
            if (
                not getattr(field, 'write_only', False) and
                not field.source == '*' and
                field.source not in model_property_names
            ):
                fields_lookups[field_name] = self.extract_source_key(
                    field.source.replace('.', '__') or field_name
                )

        return fields_lookups

    def extract_source_key(self, value: str):
        if value.startswith('get_') and value.endswith('_display'):
            return value.removeprefix('get_').removesuffix('_display')
        return value


class OrderingFilter(
    DefaultFieldExtractMixin,
    filters.OrderingFilter
):
    ordering_param = 'sort_by'
    ordering_symbol_param = 'sort_order'

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

    def map_fields_with_lookups(self, queryset, fields: list[str], view, request):
        lookups = self.get_default_fields_lookups(
            queryset, view, {'request': request}
        )

        ordering_fields_lookups_map = self.get_ordering_lookups_map(view)

        assert isinstance(
            ordering_fields_lookups_map, dict
        ), 'ordering_fields_lookups_map should be dict'

        lookups.update(ordering_fields_lookups_map)

        def trans_keys(key: str):
            prefix = '-' if key.startswith('-') else ''
            return prefix + lookups[key.lstrip('-')]

        return [
            trans_keys(field) for field in fields
            if field.lstrip('-') in lookups
        ]

    def get_odering_symbol_format(self, request, value: str):
        sort_order: str = request.query_params.get(
            self.ordering_symbol_param, 'asc'
        )

        value = value.lstrip('-')
        if sort_order.lower() == 'desc':
            return f'-{value}'

        return value

    def get_ordering_lookups_map(self, view) -> dict[str, str]:
        """
        we can add additional lookup for ordering it should be dict type
        Example:
        ```json
        ordering_fields_lookups_map={'sign_in_count': 'user_access_tracks__sign_in_count'}
        ```
        now If we add query params `?sort_by=sign_in_count` 
        it looking for `user_access_tracks__sign_in_count`
        For first level of serializer all fields work auto
        """
        return getattr(view, 'ordering_fields_lookups_map', {})


class SearchFilter(
    DefaultFieldExtractMixin,
    filters.SearchFilter
):
    search_param = 'search'

    def map_fields_with_lookups(self, queryset, fields: dict[str, str], view, request):
        lookups = self.get_default_fields_lookups(
            queryset, view, {'request': request}
        )

        search_fields_lookups_map = self.get_searching_lookups_map(view)

        assert isinstance(
            search_fields_lookups_map, dict
        ), 'search_fields_lookups_map should be dict'

        lookups.update(search_fields_lookups_map)

        return [
            (lookups[key], value) for key, value in fields.items()
            if key in lookups
        ]

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        query_fields = self.map_fields_with_lookups(
            queryset, params, view, request
        )
        if query_fields:
            return queryset.filter(**dict(query_fields))

        return super().filter_queryset(request, queryset, view)

    def get_searching_lookups_map(self, view) -> dict[str, str]:
        """
        we can add additional lookup for searching it should be dict type
        Example:
        ```json
        search_fields_lookups_map={'email': 'email__icontains'}
        ```
        now If we add query params `?email=admin` 
        it looking for `email__icontains=admin`
        For first level of serializer all fields work auto
        """
        return getattr(view, 'search_fields_lookups_map', {})
