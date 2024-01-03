## Proxy As a service - Flask (EASY)

Nothing much can be said here, The application was using flask had two routes (debug/, main route)
The debug had environment route listing env variables including the flag
The Main route requested the URL you've in the url parameter and checks if it's in a blacklist to prevent SSRF thus you've to bypass the blacklist
filter and gaining access to /debug/environment, by using 0.0.0.0, 2.2.2.2 it should work and since the application is running on 1337 the final url is

?url=@0.0.0.0:1337/debug/environment
