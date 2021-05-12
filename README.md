## Elliot
#### Hacker like communicator with implemented Signal protocol written in python

---
<br/>

![Icon of the project](elliot.png)

_mascot of the project_

--- 

Heavily inspired by the terminal chat communicator visible in 
the TV Series: MR. ROBOT.

User has access to the cli interface coloured with as much as 16 colours!!

Project under the hood is using another project: [Xavier](https://github.com/michalwilk123/xavier-chat-server) a simple REST API which 
is resposible for transporting the messages themselves over the internet.

---

Project depends on only a few dependancies:
* [aiohttp](https://github.com/aio-libs/aiohttp) - websocket connection, 
    fetching periodical data, registering users
* [cryptography](https://github.com/pyca/cryptography) - symmetric/asymetric encryption 
    between both parties and the server
* [colorama](https://github.com/tartley/colorama), [aioconsole](https://github.com/vxgmichel/aioconsole), [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu) - lighweight terminal utility packages.


The very important feature for me was that the project can run on linux and on very
limited terminal of windows. Currently only works on linux but support
for windows is planned in the future.
