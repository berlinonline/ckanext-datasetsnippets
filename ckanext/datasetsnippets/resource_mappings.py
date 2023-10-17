# encoding: utf-8
"""
Group various format strings (`CSV`, `.csv`, `zip:csv`) into abstract formats (`CSV`). Group formats (`CSV`, `XLSX`) into more general resource classes (`tabular data`). 
"""

import json
import logging
import ckan.plugins as plugins

LOG = logging.getLogger(__name__)

class ResourceMapping(plugins.SingletonPlugin):
    """
    Class representing the resource mappings.
    """

    def load_mappings(self, mappings_path: str):
        """
        Load the mappings.
        """
        self._category_mappings = {}
        try:
          with open(mappings_path) as json_data:
              self._category_mappings = json.load(json_data)
              self._format_string_mappings = self.reverse_category_mapping(self._category_mappings)
              LOG.info(self._category_mappings)
              LOG.info(self._format_string_mappings)
        except Exception:
            raise MappingsError(f"Could not load mappings from {mappings_path}.")

    def unload_mappings(self):
        """
        Unload the schema.
        """
        del self._category_mappings

    def reverse_category_mapping(self, data: dict) -> dict:
        reverse_mapping = {}
        for category, definition in data.items():
            format_strings = [format_string for group in definition['types'].values() for format_string in group]
            for format_string in format_strings:
                reverse_mapping[format_string] = category
        return reverse_mapping
        
    def category_mappings(self) -> dict:
        """
        Return the loaded resource mappings (categories -> formats -> format strings).
        """
        try:
            return self._category_mappings
        except AttributeError:
            raise MappingsError("Resource mappings file not loaded yet")

    def format_string_mappings(self) -> dict:
        """
        Return the loaded resource mappings (format_strings -> categories).
        """
        try:
            return self._format_string_mappings
        except AttributeError:
            raise MappingsError("Resource mappings file not loaded yet")

class MappingsError(Exception):
    """
    Errors when handling the mappings.
    """
