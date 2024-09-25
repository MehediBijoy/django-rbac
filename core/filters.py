from rest_framework import filters
from rest_framework.fields import Field
from rest_framework.exceptions import ValidationError

LookupType = dict[str, tuple[str, Field]]


class DefaultFieldExtractMixin:

    def build_fields_lookup(self, queryset, view, context) -> LookupType:
        serializer_class = getattr(view, 'serializer_class', None)
        model_class = queryset.model
        model_property_names = [
            attr for attr in dir(model_class)
            if isinstance(getattr(model_class, attr), property) and attr != 'pk'
        ]

        return {
            field_name: (self.extract_source_key(field.source.replace('.', '__') or field_name), field)
            for field_name, field in serializer_class(context=context).fields.items()
            if (
                not getattr(field, 'write_only', False) and
                not field.source == '*' and
                field.source not in model_property_names
            )
        }

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
                self.get_ordering_symbol_format(request, param.strip())
                for param in sort_by.split(',')
            ]
            ordering = self.map_fields_with_lookups(
                queryset, fields, view, request
            )
            if ordering:
                return ordering

        return self.get_default_ordering(view)

    def map_fields_with_lookups(self, queryset, fields: list[str], view, request):
        fields_lookups = {
            key: value[0] for key, value in
            self.build_fields_lookup(queryset, view, {'request': request}).items()
        }
        ordering_fields_lookups_map = self.get_ordering_lookups_map(view)

        assert isinstance(
            ordering_fields_lookups_map, dict
        ), 'ordering_fields_lookups_map should be dict'

        fields_lookups.update(ordering_fields_lookups_map)

        def trans_keys(key: str):
            prefix = '-' if key.startswith('-') else ''
            return prefix + fields_lookups[key.lstrip('-')]

        return [
            trans_keys(field) for field in fields
            if field.lstrip('-') in fields_lookups
        ]

    def get_ordering_symbol_format(self, request, value: str):
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

    def query_params_build(self, field_lookups: LookupType, params, search_fields: dict):
        query_params = {}

        for key, value in params.items():
            lookup = field_lookups.get(key)
            if lookup is None:
                continue

            parsed_value = self._convert_value(lookup[1], value)

            if parsed_value or search_fields.get(key):
                query_params[key] = parsed_value or value

        return query_params

    def _convert_value(self, field: Field, value):
        try:
            return field.to_internal_value(value)
        except (ValidationError, ValueError):
            return

    def map_fields_with_lookups(self, queryset, params: dict[str, str], view, request) -> list[tuple[str, any]]:
        """
        Maps query parameters to the appropriate lookup fields and values.
        """
        # Get the lookups for search fields specified in the view
        search_fields = self.get_searching_lookups_map(view)

        field_lookups = self.build_fields_lookup(queryset, view, {'request': request})
        query_params = self.query_params_build(field_lookups, params, search_fields)

        # Update with the view-specific search field lookups
        combined_lookups = {**{key: lookup[0] for key, lookup in field_lookups.items()}, **search_fields}

        return [
            (combined_lookups[key], value) for key, value in query_params.items()
            if key in combined_lookups
        ]

    def filter_queryset(self, request, queryset, view):
        query_fields = self.map_fields_with_lookups(
            queryset, request.query_params, view, request
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
        mapper = getattr(view, 'search_fields_lookups_map', {})

        assert isinstance(
            mapper, dict
        ), 'search_fields_lookups_map should be dict'

        return mapper
