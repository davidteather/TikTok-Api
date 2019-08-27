# BrowserMob Proxy

BrowserMob Proxy allows you to manipulate HTTP requests and responses, capture HTTP content, and export performance data as a [HAR file](http://www.softwareishard.com/blog/har-12-spec/).
BMP works well as a standalone proxy server, but it is especially useful when embedded in Selenium tests.

The latest version of BrowserMob Proxy is 2.1.2, powered by [LittleProxy](https://github.com/adamfisk/LittleProxy).

If you're running BrowserMob Proxy within a Java application or Selenium test, get started with [Embedded Mode](#getting-started-embedded-mode). If you want to run BMP from the
command line as a standalone proxy, start with [Standalone](#getting-started-standalone).

### Getting started: Embedded Mode
To use BrowserMob Proxy in your tests or application, add the `browsermob-core` dependency to your pom:
```xml
    <dependency>
        <groupId>net.lightbody.bmp</groupId>
        <artifactId>browsermob-core</artifactId>
        <version>2.1.2</version>
        <scope>test</scope>
    </dependency>
```

Start the proxy:
```java
    BrowserMobProxy proxy = new BrowserMobProxyServer();
    proxy.start(0);
    int port = proxy.getPort(); // get the JVM-assigned port
    // Selenium or HTTP client configuration goes here
```

Then configure your HTTP client to use a proxy running at the specified port.

**Using with Selenium?** See the [Using with Selenium](#using-with-selenium) section.

### Getting started: Standalone
To run in standalone mode from the command line, first download the latest release from the [releases page](https://github.com/lightbody/browsermob-proxy/releases), or [build the latest from source](#building-the-latest-from-source).

Start the REST API:
```sh
    ./browsermob-proxy -port 8080
```

Then create a proxy server instance:
```sh
    curl -X POST http://localhost:8080/proxy
    {"port":8081}
```

The "port" is the port of the newly-created proxy instance, so configure your HTTP client or web browser to use a proxy on the returned port.
For more information on the features available in the REST API, see [the REST API documentation](#rest-api).

## Changes since the 2.1-beta series

**The `browsermob-core-littleproxy` module is now `browsermob-core`**

After six beta releases, the LittleProxy implementation now supports more features and is more stable than the legacy implementation. To reflect that level of maturity and long-term support, the `browsermob-core` module now uses LittleProxy by default.

**Note about Legacy support**: In the 2.1-betas, if you were using the `ProxyServer` or `LegacyProxyServer` classes, use the `browsermob-core-legacy` module in 2.1.0 and higher.

*LittleProxy support for `LegacyProxyServer` has moved to `BrowserMobProxyServerLegacyAdapter`*. Using the LittleProxy implementation with the `LegacyProxyServer` interface is still fully supported as a means to help you transition from 2.0.0. Unlike the 2.1-beta series, the `BrowserMobProxyServer` class
no longer implements `LegacyProxyServer`; however, the `BrowserMobProxyServerLegacyAdapter` can be used to integrate legacy code with the new LittleProxy interface. You must still use the `browsermob-core-legacy` module when using the LegacyAdapter.

```java
   LegacyProxyServer proxy = new BrowserMobProxyServerLegacyAdapter();
   proxy.setPort(8081); // method only supported by the legacy interface
   proxy.start();
```

## Changes since 2.0.0

The new [BrowserMobProxyServer class](browsermob-core/src/main/java/net/lightbody/bmp/BrowserMobProxyServer.java) has replaced the legacy ProxyServer implementation. The legacy implementation is no longer actively supported; all new code should use `BrowserMobProxyServer`. We highly recommend that existing code migrate to the new implementation.

The most important changes from 2.0 are:

- [Separate REST API and Embedded Mode modules](#embedded-mode). Include only the functionality you need.
- [New BrowserMobProxy interface](browsermob-core/src/main/java/net/lightbody/bmp/BrowserMobProxy.java). The new interface will completely replace the legacy 2.0 ProxyServer contract in version 3.0 and higher.
- [LittleProxy support](#littleproxy-support). More stable and more powerful than the legacy Jetty back-end.

### New BrowserMobProxy API

BrowserMob Proxy 2.1 includes a [new BrowserMobProxy interface](browsermob-core/src/main/java/net/lightbody/bmp/BrowserMobProxy.java) to interact with BrowserMob Proxy programmatically. The new interface defines the functionality that BrowserMob Proxy will support in future releases (including 3.0+). To ease migration, both the legacy (Jetty-based) ProxyServer class and the new, LittleProxy-powered BrowserMobProxy class support the new BrowserMobProxy interface.

We _highly_ recommend migrating existing code to the BrowserMobProxy interface using the `BrowserMobProxyServer` class.

### Using the LittleProxy implementation with 2.0.0 code

The legacy interface, implicitly defined by the ProxyServer class, has been extracted into `net.lightbody.bmp.proxy.LegacyProxyServer` and is now officially deprecated. The new LittleProxy-based implementation will implement LegacyProxyServer for all 2.1.x releases. This means you can switch to the LittleProxy-powered implementation with minimal change to existing code ([with the exception of interceptors](#http-request-manipulation)):

```java
    // With the Jetty-based 2.0.0 release, BMP was created like this:
    ProxyServer proxyServer = new ProxyServer();
    proxyServer.start();
    // [...]

    // To use the LittleProxy-powered 2.1.2 release, simply change to
    // the LegacyProxyServer interface and the adapter for the new
    // LittleProxy-based implementation:
    LegacyProxyServer proxyServer = new BrowserMobProxyServerLegacyAdapter();
    proxyServer.start();
    // Almost all deprecated 2.0.0 methods are supported by the 
    // new BrowserMobProxyServerLegacyAdapter implementation, so in most cases,
    // no further code changes are necessary
```

LegacyProxyServer will not be supported after 3.0 is released, so we recommend migrating to the `BrowserMobProxy` interface as soon as possible. The new interface provides additional functionality and is compatible with both the legacy Jetty-based ProxyServer implementation [(with some exceptions)](new-interface-compatibility.md) and the new LittleProxy implementation.

If you must continue using the legacy Jetty-based implementation, include the `browsermob-core-legacy` artifact instead of `browsermob-core`.

## Features and Usage

The proxy is programmatically controlled via a REST interface or by being embedded directly inside Java-based programs and unit tests. It captures performance data in the [HAR format](http://groups.google.com/group/http-archive-specification). In addition it can actually control HTTP traffic, such as:

 - blacklisting and whitelisting certain URL patterns
 - simulating various bandwidth and latency
 - remapping DNS lookups
 - flushing DNS caching
 - controlling DNS and request timeouts
 - automatic BASIC authorization

### REST API

**New in 2.1:** The REST API now supports LittleProxy. As of 2.1.0-beta-3, LittleProxy is the default implementation. (You may specify `--use-littleproxy false` to disable LittleProxy in favor of the legacy Jetty 5-based implementation.)

To get started, first start the proxy by running `browsermob-proxy` or `browsermob-proxy.bat` in the bin directory:

    $ sh browsermob-proxy -port 8080
    INFO 05/31 03:12:48 o.b.p.Main           - Starting up...
    2011-05-30 20:12:49.517:INFO::jetty-7.3.0.v20110203
    2011-05-30 20:12:49.689:INFO::started o.e.j.s.ServletContextHandler{/,null}
    2011-05-30 20:12:49.820:INFO::Started SelectChannelConnector@0.0.0.0:8080

Once started, there won't be an actual proxy running until you create a new proxy. You can do this by POSTing to /proxy:

    [~]$ curl -X POST http://localhost:8080/proxy
    {"port":8081}

or optionally specify your own port:

    [~]$ curl -X POST -d 'port=8089' http://localhost:8080/proxy
    {"port":8089}

or if running BrowserMob Proxy in a multi-homed environment, specify a desired bind address (default is `0.0.0.0`):

    [~]$ curl -X POST -d 'bindAddress=192.168.1.222' http://localhost:8080/proxy
    {"port":8086}

Once that is done, a new proxy will be available on the port returned. All you have to do is point a browser to that proxy on that port and you should be able to browse the internet. The following additional APIs will then be available:

Description |  HTTP method | Request path | Request parameters
--- | :---: | :---: | ---
Get a list of ports attached to `ProxyServer` instances managed by `ProxyManager` | GET | */proxy* || 
<a name="harcreate">Creates a new HAR</a> attached to the proxy and returns the HAR content if there was a previous HAR. *[port]* in request path it is port where your proxy was started | PUT |*/proxy/[port]/har* |<p>*captureHeaders* - Boolean, capture headers or not. Optional, default to "false".</p><p>*captureContent* - Boolean, capture content bodies or not. Optional, default to "false".</p><p>*captureBinaryContent* - Boolean, capture binary content or not. Optional, default to "false".</p><p>*initialPageRef* - The string name of The first page ref that should be used in the HAR. Optional, default to "Page 1".</p><p>*initialPageTitle* - The title of first HAR page. Optional, default to *initialPageRef*.</p>
Starts a new page on the existing HAR. *[port]* in request path it is port where your proxy was started | PUT | */proxy/[port]/har/pageRef* |<p>*pageRef* - The string name of the first page ref that should be used in the HAR. Optional, default to "Page N" where N is the next page number.</p><p>*pageTitle* - The title of new HAR page. Optional, default to `pageRef`.</p>
Shuts down the proxy and closes the port. *[port]* in request path it is port where your proxy was started | DELETE | */proxy/[port]* ||
Returns the JSON/HAR content representing all the HTTP traffic passed through the proxy (provided you have already created the HAR with [this method](#harcreate)) | GET | */proxy/[port]/har* ||
Displays whitelisted items | GET | */proxy/[port]/whitelist* ||
Sets a list of URL patterns to whitelist | PUT | */proxy/[port]/whitelist* |<p>*regex* - A comma separated list of regular expressions.</p><p>*status* - The HTTP status code to return for URLs that do not match the whitelist.</p>|
Clears all URL patterns from the whitelist  | DELETE | */proxy/[port]/whitelist* ||
Displays blacklisted items | GET | */proxy/[port]/blacklist* ||
Set a URL to blacklist | PUT | */proxy/[port]/blacklist* |<p>*regex* - The blacklist regular expression.</p><p>*status* - The HTTP status code to return for URLs that are blacklisted.</p><p>*method* - The regular expression for matching HTTP method (GET, POST, PUT, etc). Optional, by default processing all HTTP method.</p>|
Clears all URL patterns from the blacklist | DELETE | */proxy/[port]/blacklist* ||
Limit the bandwidth through the proxy on the *[port]* | PUT | */proxy/[port]/limit* |<p>*downstreamKbps* - Sets the downstream bandwidth limit in kbps. Optional.</p><p>*upstreamKbps* - Sets the upstream bandwidth limit kbps. Optional, by default unlimited.</p><p>*downstreamMaxKB* - Specifies how many kilobytes in total the client is allowed to download through the proxy. Optional, by default unlimited.</p><p>*upstreamMaxKB* - Specifies how many kilobytes in total the client is allowed to upload through the proxy. Optional, by default unlimited.</p><p>*latency* - Add the given latency to each HTTP request. Optional, by default all requests are invoked without latency.</p><p>*enable* - A boolean that enable bandwidth limiter. Optional, by default to "false", but setting any of the properties above will implicitly enable throttling</p><p>*payloadPercentage* - Specifying what percentage of data sent is payload, e.g. use this to take into account overhead due to tcp/ip. Optional.</p><p>*maxBitsPerSecond* - The max bits per seconds you want this instance of StreamManager to respect. Optional.</p>
Displays the amount of data remaining to be uploaded/downloaded until the limit is reached | GET | */proxy/[port]/limit* ||
Set and override HTTP Request headers | POST | */proxy/[port]/headers* | Payload data should be **JSON** encoded set of headers. Where key is a header name (such as "User-Agent") and  value is a value of HTTP header to setup (such as "BrowserMob-Agent"). Example: `{"User-Agent": "BrowserMob-Agent"}`|
Overrides normal DNS lookups and remaps the given hosts with the associated IP address | POST | */proxy/[port]/hosts* | Payload data should be **JSON** encoded set of hosts. Where key is a host name (such as "example.com") and value is a IP address which associatied with host hame (such as "1.2.3.4"'). Example: `{"example.com": "1.2.3.4"}`|
Sets automatic basic authentication for the specified domain | POST | */proxy/[port]/auth/basic/[domain]* | Payload data should be **JSON** encoded username and password name/value pairs. Example: `{"username": "myUsername", "password": "myPassword"}`|
Wait till all request are being made | PUT | */proxy/[port]/wait* |<p>*quietPeriodInMs* - Wait till all request are being made. Optional.</p><p>*timeoutInMs* - Sets quiet period in milliseconds. Optional.</p>|
Handles different proxy timeouts | PUT | *proxy/[port]/timeout* |<p>Payload data should be **JSON** encoded set of parameters. Where key is a parameters name (such as "connectionTimeout") and  value is a value of parameter to setup (such as "500")</p><p>*requestTimeout* - Request timeout in milliseconds. A timeout value of -1 is interpreted as infinite timeout. Optional, default to "-1".</p><p>*readTimeout* - Read timeout in milliseconds. Which is the timeout for waiting for data or, put differently, a maximum period inactivity between two consecutive data packets). A timeout value of zero is interpreted as an infinite timeout. Optional, default to "60000".</p><p>*connectionTimeout* - Determines the timeout in milliseconds until a connection is established. A timeout value of zero is interpreted as an infinite timeout. Optional, default to "60000".</p><p>*dnsCacheTimeout* - Sets the maximum length of time that records will be stored in this Cache. A nonpositive value disables this feature (that is, sets no limit). Optional, default to "0".</p>Example: `{"connectionTimeout" : "500", "readTimeout" : "200"}`|
Redirecting URL's | PUT | */proxy/[port]/rewrite* |<p>*matchRegex* - A matching URL regular expression.</p><p>*replace* - replacement URL.</p>|
Removes all URL redirection rules currently in effect | DELETE | */proxy/[port]/rewrite* ||
Setting the retry count | PUT | */proxy/[port]/retry* |<p>*retrycount* - The number of times a method will be retried.</p>|
Empties the DNS cache | DELETE | */proxy/[port]/dns/cache* ||
| [REST API interceptors with LittleProxy](#interceptorsRESTapiLP) |||
|Describe your own request interception | POST | */proxy/[port]/filter/request* | A string wich determinates interceptor rules. See more [here](#interceptorsRESTapiLPRequestFilter) |
|Describe your own response interception | POST | */proxy/[port]/filter/response* | A string wich determinates interceptor rules. See more [here](#interceptorsRESTapiLPResponseFilter) |
| [REST API with Legacy interceptors](#interceptorsRESTapiLegacy) ||||
|Describe your own request interception | POST | */proxy/[port]/interceptor/request* | A string wich determinates interceptor rules. See more [here](#interceptorsRESTapiLegacy) |
|Describe your own response interception | POST | */proxy/[port]/interceptor/response* | A string wich determinates interceptor rules. See more [here](#interceptorsRESTapiLegacy) |

For example, once you've started the proxy you can create a new HAR to start recording data like so:

    [~]$ curl -X PUT -d 'initialPageRef=Foo' http://localhost:8080/proxy/8081/har

Now when traffic goes through port 9091 it will be attached to a page reference named "Foo". Consult the HAR specification for more info on what a "pageRef" is. You can also start a new pageRef like so:

    [~]$ curl -X PUT -d 'pageRef=Bar' http://localhost:8080/proxy/8081/har/pageRef

That will ensure no more HTTP requests get attached to the old pageRef (Foo) and start getting attached to the new pageRef (Bar). After creating the HAR, you can get its content at any time like so:

    [~]$ curl http://localhost:8080/proxy/8081/har

Sometimes you will want to route requests through an upstream proxy server. In this case specify your proxy server by adding the httpProxy parameter to your create proxy request:

    [~]$ curl -X POST http://localhost:8080/proxy?httpProxy=yourproxyserver.com:8080
    {"port":8081}

Alternatively, you can specify the upstream proxy config for all proxies created using the standard JVM [system properties for HTTP proxies](http://docs.oracle.com/javase/6/docs/technotes/guides/net/proxies.html).
Note that you can still override the default upstream proxy via the POST payload, but if you omit the payload the JVM
system properties will be used to specify the upstream proxy.

### Command-line Arguments

 - -port \<port\>
  - Port on which the API listens. Default value is 8080.
 - -address <address>
  - Address to which the API is bound. Default value is 0.0.0.0.
 - -proxyPortRange \<from\>-\<to\>
  - Range of ports reserved for proxies. Only applies if *port* parameter is not supplied in the POST request. Default values are \<port\>+1 to \<port\>+500+1.
 - -ttl \<seconds\>
  - Proxy will be automatically deleted after a specified time period. Off by default.

### Embedded Mode

**New in 2.1:** New Embedded Mode module

**New in 2.1:** New [BrowserMobProxy interface](#new-browsermobproxy-api) for Embedded Mode

BrowserMob Proxy 2.1 separates the Embedded Mode and REST API into two modules. If you only need Embedded Mode functionality, add the `browsermob-core` artifact as a dependency. The REST API artifact is `browsermob-rest`.

If you're using Java and Selenium, the easiest way to get started is to embed the project directly in your test. First, you'll need to make sure that all the dependencies are imported in to the project. You can find them in the *lib* directory. Or, if you're using Maven, you can add this to your pom:
```xml
    <dependency>
        <groupId>net.lightbody.bmp</groupId>
        <artifactId>browsermob-core</artifactId>
        <version>2.1.2</version>
        <scope>test</scope>
    </dependency>
```

Once done, you can start a proxy using `net.lightbody.bmp.BrowserMobProxy`:
```java
    BrowserMobProxy proxy = new BrowserMobProxyServer();
    proxy.start(0);
    // get the JVM-assigned port and get to work!
    int port = proxy.getPort();
    //...
```

Consult the Javadocs on the `net.lightbody.bmp.BrowserMobProxy` class for the full API.

### Using With Selenium

BrowserMob Proxy makes it easy to use a proxy in Selenium tests:
```java
    // start the proxy
    BrowserMobProxy proxy = new BrowserMobProxyServer();
    proxy.start(0);

    // get the Selenium proxy object
    Proxy seleniumProxy = ClientUtil.createSeleniumProxy(proxy);

    // configure it as a desired capability
    DesiredCapabilities capabilities = new DesiredCapabilities();
    capabilities.setCapability(CapabilityType.PROXY, seleniumProxy);

    // start the browser up
    WebDriver driver = new FirefoxDriver(capabilities);

    // enable more detailed HAR capture, if desired (see CaptureType for the complete list)
    proxy.enableHarCaptureTypes(CaptureType.REQUEST_CONTENT, CaptureType.RESPONSE_CONTENT);

    // create a new HAR with the label "yahoo.com"
    proxy.newHar("yahoo.com");

    // open yahoo.com
    driver.get("http://yahoo.com");

    // get the HAR data
    Har har = proxy.getHar();
```

**Note**: If you're running running tests on a Selenium grid, you will need to customize the Selenium Proxy object
created by `createSeleniumProxy()` to point to the hostname of the machine that your test is running on. You can also run a standalone
BrowserMob Proxy instance on a separate machine and configure the Selenium Proxy object to use that proxy.

### HTTP Request Manipulation

**HTTP request manipulation has changed in 2.1.0+ with LittleProxy.** The LittleProxy-based interceptors are easier to use and more reliable. The legacy ProxyServer implementation **will not** support the new interceptor methods.

#### 2.1.0+ (LittleProxy) interceptors

There are four new methods to support request and response interception in LittleProxy:

  - `addRequestFilter`
  - `addResponseFilter`
  - `addFirstHttpFilterFactory`
  - `addLastHttpFilterFactory`

For most use cases, including inspecting and modifying requests/responses, `addRequestFilter` and `addResponseFilter` will be sufficient. The request and response filters are easy to use:
```java
    proxy.addRequestFilter(new RequestFilter() {
            @Override
            public HttpResponse filterRequest(HttpRequest request, HttpMessageContents contents, HttpMessageInfo messageInfo) {
                if (messageInfo.getOriginalUri().endsWith("/some-endpoint-to-intercept")) {
                    // retrieve the existing message contents as a String or, for binary contents, as a byte[]
                    String messageContents = contents.getTextContents();

                    // do some manipulation of the contents
                    String newContents = messageContents.replaceAll("original-string", "my-modified-string");
                    //[...]

                    // replace the existing content by calling setTextContents() or setBinaryContents()
                    contents.setTextContents(newContents);
                }

                // in the request filter, you can return an HttpResponse object to "short-circuit" the request
                return null;
            }
        });
        
        // responses are equally as simple:
        proxy.addResponseFilter(new ResponseFilter() {
            @Override
            public void filterResponse(HttpResponse response, HttpMessageContents contents, HttpMessageInfo messageInfo) {
                if (/*...some filtering criteria...*/) {
                    contents.setTextContents("This message body will appear in all responses!");
                }
            }
        });
```

With Java 8, the syntax is even more concise:
```java
        proxy.addResponseFilter((response, contents, messageInfo) -> {
            if (/*...some filtering criteria...*/) {
                contents.setTextContents("This message body will appear in all responses!");
            }
        });
```

See the javadoc for the `RequestFilter` and `ResponseFilter` classes for more information.

For fine-grained control over the request and response lifecycle, you can add "filter factories" directly using `addFirstHttpFilterFactory` and `addLastHttpFilterFactory` (see the examples in the InterceptorTest unit tests).

#### <a name="interceptorsRESTapiLP">REST API interceptors with LittleProxy</a>

When running the REST API with LittleProxy enabled, you cannot use the legacy `/:port/interceptor/` endpoints. Instead, POST the javascript payload to the new `/:port/filter/request` and `/:port/filter/response` endpoints.

##### <a name="interceptorsRESTapiLPRequestFilter">Request filters</a>

Javascript request filters have access to the variables `request` (type `io.netty.handler.codec.http.HttpRequest`), `contents` (type `net.lightbody.bmp.util.HttpMessageContents`), and `messageInfo` (type `net.lightbody.bmp.util.HttpMessageInfo`). `messageInfo` contains additional information about the message, including whether the message is sent over HTTP or HTTPS, as well as the original request received from the client before any changes made by previous filters. If the javascript returns an object of type `io.netty.handler.codec.http.HttpResponse`, the HTTP request will "short-circuit" and return the response immediately.

**Example: Modify User-Agent header**

```sh
curl -i -X POST -H 'Content-Type: text/plain' -d "request.headers().remove('User-Agent'); request.headers().add('User-Agent', 'My-Custom-User-Agent-String 1.0');" http://localhost:8080/proxy/8081/filter/request
```

##### <a name="interceptorsRESTapiLPResponseFilter">Response filters</a>

Javascript response filters have access to the variables `response` (type `io.netty.handler.codec.http.HttpResponse`), `contents` (type `net.lightbody.bmp.util.HttpMessageContents`), and `messageInfo` (type `net.lightbody.bmp.util.HttpMessageInfo`). As in the request filter, `messageInfo` contains additional information about the message.

**Example: Modify response body**

```sh
curl -i -X POST -H 'Content-Type: text/plain' -d "contents.setTextContents('<html><body>Response successfully intercepted</body></html>');" http://localhost:8080/proxy/8081/filter/response
```

#### Legacy interceptors

If you are using the legacy ProxyServer implementation, you can manipulate the requests like so:
```java
    BrowserMobProxy server = new ProxyServer();
    ((LegacyProxyServer)server).addRequestInterceptor(new RequestInterceptor() {
        @Override
        public void process(BrowserMobHttpRequest request, Har har) {
            request.getMethod().removeHeaders("User-Agent");
            request.getMethod().addHeader("User-Agent", "Bananabot/1.0");
        }
    });
```
<a name="interceptorsRESTapiLegacy"></a>You can also POST a JavaScript payload to `/:port/interceptor/request` and `/:port/interceptor/response` using the REST interface. The functions will have a `request`/`response` variable, respectively, and a `har` variable (which may be null if a HAR isn't set up yet). The JavaScript code will be run by [Rhino](https://github.com/mozilla/rhino) and have access to the same Java API in the example above:

    [~]$ curl -X POST -H 'Content-Type: text/plain' -d 'request.getMethod().removeHeaders("User-Agent");' http://localhost:8080/proxy/8081/interceptor/request
    
Consult the Java API docs for more info.

### SSL Support

**BrowserMob Proxy 2.1.0+ now supports full MITM:** For most users, MITM will work out-of-the-box with default settings. Install the [ca-certificate-rsa.cer](/browsermob-core/src/main/resources/sslSupport/ca-certificate-rsa.cer) file in your browser or HTTP client to avoid untrusted certificate warnings. Generally, it is safer to generate your own private key, rather than using the .cer files distributed with BrowserMob Proxy. See the [README file in the `mitm` module](/mitm/README.md) for instructions on generating or using your own root certificate and private key with MITM.

**Legacy Jetty-based ProxyServer support for MITM:** The legacy `ProxyServer` implementation uses the same `ca-certificate-rsa.cer` root certificate as the default BrowserMobProxyServer implementation. The previous cybervillainsCA.cer certificate has been removed.

**Note: DO NOT** permanently install the .cer files distributed with BrowserMob Proxy in users' browsers. They should be used for testing only and must not be used with general web browsing.

If you're doing testing with Selenium, you'll want to make sure that the browser profile that gets set up by Selenium not only has the proxy configured, but also has the CA installed. Unfortunately, there is no API for doing this in Selenium; it must be done manually for each browser and environment.

### NodeJS Support

NodeJS bindings for browswermob-proxy are available [here](https://github.com/zzo/browsermob-node).  Built-in support for [Selenium](http://seleniumhq.org) or use [CapserJS-on-PhantomJS](http://casperjs.org) or anything else to drive traffic for HAR generation.

### Logging

When running in stand-alone mode, the proxy loads the default logging configuration from the conf/bmp-logging.yaml file. To increase/decrease the logging level, change the logging entry for net.lightbody.bmp.

### DNS Resolution

The BrowserMobProxyServer implementation uses native DNS resolution by default, but supports custom DNS resolution and advanced DNS manipulation. See the [ClientUtil](browsermob-proxy/browsermob-core/src/main/java/net/lightbody/bmp/client/ClientUtil.java) class for information on DNS manipulation using the dnsjava resolver.

## Building the latest from source

You'll need maven (`brew install maven` if you're on OS X):

    [~]$ mvn -DskipTests
    
You'll find the standalone BrowserMob Proxy distributable zip at `browsermob-dist/target/browsermob-proxy-2.1.3-SNAPSHOT-bin.zip`. Unzip the contents and run the `browsermob-proxy` or `browsermob-proxy.bat` files in the `bin` directory.

When you build the latest code from source, you'll have access to the latest snapshot release. To use the SNAPSHOT version in your code, modify the version in your pom:
```xml
    <dependency>
        <groupId>net.lightbody.bmp</groupId>
        <artifactId>browsermob-core</artifactId>
        <version>2.1.3-SNAPSHOT</version>
        <scope>test</scope>
    </dependency>
```
