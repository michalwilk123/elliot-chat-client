## Elliot
#### hacker like comunnicator with implemented Signal protocol


---
<br/>

![Icon of the project](elliot.png)

_mascot of the project_

Chat communicator inspired by the chat communicator visible in the TV Series: MR. ROBOT.

User has access to the cli interface coloured with as much as 16 colours!!

The very important feature for me was that the project can run on linux and 
limited terminal of windows. Currently only works under the linux but support
for windows is planned.

Project under the hood uses another project: [Xavier]() a simple REST API which 
is resposible for transporting the messages themselves over the internet.

Project depends on only few dependancies:
* [aiohttp](https://github.com/aio-libs/aiohttp) - websocket connection, 
    fetching periodical data, registering users
* [cryptography](https://github.com/pyca/cryptography) - symmetric/asymetric encryption 
    between both parties and the server
* [colorama](https://github.com/tartley/colorama), [aioconsole](https://github.com/vxgmichel/aioconsole), [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu) - lighweight terminal packages