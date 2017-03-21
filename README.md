# resilient-requests

The goal of this library is to implement a resilient version of the [requests](http://docs.python-requests.org/en/master/) library.
 
This library will support:

1. Timeouts (already supported by [requests](http://docs.python-requests.org/en/master/))
2. Retry (via [HttpAdapter](http://docs.python-requests.org/en/master/api/#requests.adapters.HTTPAdapter), using urllib3 [Retry](http://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry) class)

## Usage
Eventually the interface should be something like this:

``` python
requests.get(url, timeout=(connect_seconds, read_seconds), retry=(total, backoff_factor, status_forcelist))
```

For example:
``` python
requests.get('https://example.com/posts', timeout=(2, 1), retry=(3, 0.1, [500, 501]))
```