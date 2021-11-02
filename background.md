Hello everyone!

I am trying to implement a really simple echo client/server utilizing AHF for finding the partner. I know that there are already many examples of how to use AHF, but I see them still as quite complex. (And some of them are even not working properly, so it is quite hard to debug when you have no idea what should actually happen.)

I am using 4.3.0 (as 4.4.0 is still not released).

If I understand everything correctly, both parts should behave as follows (skipping certificate generation):

*Server*
1. Register the system + service. Send data to `serviceregistry/register`, e.g.
```
{
    "interfaces": [
        "HTTP-INSECURE-JSON",
    ],
    "providerSystem": {
        "systemName": "echo_server",
        "authenticationInfo": PUBLIC_KEY,
        "address": "127.0.0.1",
        "port": 34597,
    },
    "serviceDefinition": "echo",
    "secure": "CERTIFICATE",
    "version": 1,
}
```
If this fails, skip to 4 and then retry. As it is probably already registered from previous try.

2. Remember the interface ID, provider ID and service ID from the response. (Required later.)

3. Start up the echo server. Wait until exit.

4. Unregister the service. Send data to `serviceregistry/unregister`, e.g.
```
{
    "address": "127.0.0.1",
    "port": 34597,
    "system_name": "echo_server",
    "service_definition": "echo",
}
```

*Client*
Look for the server. Send data to `orchestrator/orchestration`, e.g.
```
{
    "requesterSystem": {
        "systemName": "echo_client",
        "authenticationInfo": PUBLIC_KEY,
        "address": "127.0.0.1",
        "port": 0,
    },
    "orchestrationFlags": {
        "overrideStore": "true"
    },
    "requestedService": {
        "serviceDefinitionRequirement": "echo",
    }
}
```

If this fails, the client is not authorized to do this. So it needs to be
registered first. There are (at least?) 3 ways how to do it:

a. (Externally) Using sysop access; `serviceregistry/mgmt/systems`,
```
{
    "systemName": "echo_client",
    "authenticationInfo": PUBLIC_KEY,
    "address": "127.0.0.1",
    "port": 0,
}
```
Which returns also the consumer ID.

b. (Workaround) Using `serviceregistry/register` and create a dummy service,
```
{
    "interfaces": [
        "HTTP-INSECURE-JSON",
    ],
    "providerSystem": {
        "systemName": "echo_client",
        "authenticationInfo": PUBLIC_KEY,
        "address": "127.0.0.1",
        "port": 0,
    },
    "serviceDefinition": "dummy",
    "secure": "CERTIFICATE",
    "version": 1,
}
```
Which returns the provider ID we treat as consumer ID.

c. (Undocumented) Using `serviceregistry/register-system`.
```
{
    "systemName": "echo_client",
    "authenticationInfo": PUBLIC_KEY,
    "address": "127.0.0.1",
    "port": 0,
}
```
Which also returns provider ID.


After the system is registered we can retry the orchestration. However,
there is **no way how to receive the consumer ID from the client** when
it is already registered.

If a server is found, we retrieve its IP and PORT and connect to it. Otherwise,
we need to add an authorization (intracloud) rule using sysop to `authorization/mgmt/intracloud`, e.g.
```
{
    "consumerId": consumerID,
    "interfaceIds": [
        interfaceID,
    ],
    "providerIds": [
        providerID,
    ],
    "serviceDefinitionIds": [
        serviceID,
    ],
}
```


Is it correct to interact with AHF this way, or should I also use other core systems?
If so, is there any manual on what should be done?

Thanks for replies!
