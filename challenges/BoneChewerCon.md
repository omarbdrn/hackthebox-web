## BoneChewerCon - Hard
Link : https://app.hackthebox.com/challenges/bonechewercon

After downloading the necessary files for the challenge i've started looking how the app works and what it is supposed to do.
at first glance you know it's about JWT Token Forging because of the `models.py` file
```python
def get_jwk(url, kid):
		jwks = session.fetch_jku(url)

		if not jwks or not isinstance(jwks, dict):
			return abort(400, 'Invalid jwk response')

		public_keys = {}

		for jwk in jwks.get('keys'):

			if not jwk['alg'] == 'RS256':
				return abort(400, 'Invalid key algorithm')

			if not set(('e', 'n')).issubset(jwk):
				return abort(400, 'Missing exponent and/or modulus')

			for field in ['e', 'n']:
				if jwk[field].isdigit():
					jwk[field] = jwt.utils.to_base64url_uint(int(jwk[field])).decode()
				else:
					return abort(400, 'Invalid exponent and/or modulus')


			public_keys[jwk['kid']] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

		if kid not in public_keys:
			return abort(400, 'Invalid key-id')
	
		return public_keys[kid]
```
Of course `JKU` header, if you are not familiar with JKU header or JWT tokens check it out [Auth0 Post](https://auth0.com/learn/json-web-tokens/).

### Part 1 JKU Claim Misuse
When using `JKU` header in `JWT` tokens you need `jwks.json` and that file contains the signature (n,e) that is being verified with the public and private keys used to sign the token [RFC](https://datatracker.ietf.org/doc/html/rfc7515),
by decoding our current **JWT token** in [JWT.io](https://jwt.io/)

![image](https://user-images.githubusercontent.com/32434709/140855160-873f050e-7e30-4b67-9485-9c50464257be.png)

The algorithm used is [RS256](https://community.auth0.com/t/jwt-signing-algorithms-rs256-vs-hs256/7720/2)
Since our goal is to list presentations for the user `admin` let's forge a token by creating our own public and private keys, use [RSA 2048 bit Generator](https://travistidwell.com/jsencrypt/demo/)
and then save the Public Key to `pkey.txt` and extract the signature (n,e) from it by using the following exploit
```python
from Crypto.PublicKey import RSA
fp = open("pkey.txt", "r")
key = RSA.importKey(fp.read())
fp.close()
print("n:", hex(key.n))
print("e:", hex(key.e)) # 65537
```
and then sign the token with your private and public keys and change the jku header to your server

![image](https://user-images.githubusercontent.com/32434709/140856691-35adb528-4e64-4edb-ad22-58182855aa71.png)

Now we're ready with our forged token change the `auth` cookie and refresh the `/list` endpoint *oh sorry forgot to tell you to read the god damn source code yourself.*

![image](https://user-images.githubusercontent.com/32434709/140856863-217214f1-8225-4dae-853f-6cce603fdb22.png)

Hmmm. Let's search for the error in the source code

![image](https://user-images.githubusercontent.com/32434709/140856942-6f6d0004-7107-406f-9fc8-fed4b81af614.png)

ok we can't bypass that so let's review the source code again to see any other vulnerability to chain this with, we will be looking for SSRF, XSS

![image](https://user-images.githubusercontent.com/32434709/140857315-b4f31aa8-6e4a-4822-b447-1ff45ff85d49.png)

After a bit of searching i've found XSS in the submissions/list page, prettify obvious since all we can control is our Submission and the Admin token so currently we need a working XSS Payload
so fire up that docker on your vps and start building your payload.

**Security Polciy (CSP)**
You'll hang up on this a bit but as a hint you will find your token from JWT token (Fig 1.) and by editing the token you can edit the CSP Header and whitelist your domain.

Done building your payload? Congrats you've hacked yourself now let's find a way to bypass the CSP Header in the `admin` user `(HINT: bot.js)`
This is the tricky part ( not finished, still writing )

