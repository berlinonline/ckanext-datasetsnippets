# Adding a New Virtual Resource

A virtual resource is a resource that is not actually a resource in the dataset's metadata, but one that gets added to the output page, based on some heuristics.
A virtual resource would be a link that is helpful to end users, but not actually part of the data.
An example is the WFS-explorer link that can be added automatically to all WFS datasets.

The following steps are necessary for adding a virtual resource:

## Helper Function

Define a function that determines whether or not to add the resource.
The example for the WFS explorer in [ckanext/datasetsnippets/helpers.py](ckanext/datasetsnippets/helpers.py):

```python
def wfs_endpoint_for_dataset(dataset_dict: dict) -> str:
    '''Returns the WFS endpoint for a dataset. If the dataset is not a WFS,
    or doesn't have a resource that looks like an API endpoint, return `None`.'''
    for resource in dataset_dict['resources']:
        if resource.get('format') and resource['format'].upper() == "WFS":
            if resource.get('internal_function') == 'api_endpoint':
                if resource.get('url'):
                    return resource['url']
    return None
```

