# Code for the ARAX Pilot software 

### Subdirectory `ARAXQuery`

- Contains the classes for controlling the ARAX components.

### Subdirectory `Testing`

- Some simple testing scripts.

### General recommendations about the system in development

- Care should be taken that the code never just dies because then there is no feedback about the problem in the API/UI
- Use the response.error mechanism. Always set up a response object and always return it
    - DEBUG: Only something an ARAX team member would want to see
    - INFO: Something an API user might like to see to examine the steps behind the scenes. Good for innocuous assumptions.
    - WARNING: Something that an API user should sit up and notice. Good for assumptions with impact
    - ERROR: A failure that prevents fulfilling the request. Note that logging an error may not halt processing. Several can accumulate

General response paradigm:
- Major methods (not little helper ones that can't fail) and calls to different ARAX classes should always:
	- Instantiate a Response() object
	- Log with response.debug, response.info, response.warning, response.error
	- Place returned data objects in the response.data envelope (dict)
	- always return the response object
- Callers of major methods should call with result = object.method()
- Then immediately merge the new result into active response
- Then immediately check result.status to make sure it is 'OK', and if not, return response or take some other action for method call failure

- The class may store the Response object as an object variable and sharing it among the methods that way (this may be convenient)

- The major ARAX-Filter, ARAX-Overlay, ARAX-Expander classes are stubbed out. Use those. But feel free to create lots of
  other helper classes in other files. All functionality need not (and probably should not) be all in one file