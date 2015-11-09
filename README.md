pyzzle
=======
* pyren
```
    pyren is an application that helps send an http request to the specified
    web site and handles the response per the definition in config file.
    the config file defines the method, url and data for the request, and the
    handler to handle the response, the field refresh_log tells it whether to
    write a refresh log into the log folder.
    beblow a example of the config file:
      {
      "method" : "post",
      "url": "http://url.to/api/foobar", 
      "data": {"name": "value"}, 
      "handler": "on_refresh_character", 
      "refresh_log": "yes", 
      "__end__": ""
      }
```



