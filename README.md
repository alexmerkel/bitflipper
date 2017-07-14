bitflipper
==========

What is bitflipper
------------------

bitflipper is a small python script that takes a domain name as input and prints a list of all valid domain names derived from the input by flipping one bit. It can also use the [domainr](https://domainr.build/) API to check which of the derived domains are available.


domainr API Key
---------------

In order automatically check the status of the derived domains, a domainr API key is required. You can get one [for free](https://market.mashape.com/domainr/domainr/pricing).
The key has to be added to a file called ```.bitflipper``` in your home directory:
```
$ echo "DOMAINR-API=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > ~/.bitflipper
```
where ```xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx``` is replaced by your API key.


Requirements
------------

*   [colored package](https://pypi.python.org/pypi/colored)


License
-------

MIT
