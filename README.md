# Simple echo provider+consumer using Arrowhead Framework

This repository contains simple echo provider and consumer as an example for using Arrowhead Framework.

It is designed to use `testcloud2` configuration from the [core-java-spring](https://github.com/eclipse-arrowhead/core-java-spring) repository. Therefore, it should be much easier to test this locally, as all required certificates are already created.

The reason for using `testcloud2` instead of `testcloud1` is, that the latter one had some naming issues inside the certificates.

In addition, because of [#202](https://github.com/eclipse-arrowhead/core-java-spring/issues/202) underscores are not supported in Arrowhead Framework 4.4.0+ (not supported in DNS/CN). To avoid issues we won't use even dashes, because who knows.

## Downloading required packages

This version requires Python 3 with only one additional package:

```sh
python3 -m pip install requests-pkcs12
```

## Setting up the certificates
**TODO: Use already generated certificates to make this even easier.**

At first, you have to download the CertificateGeneration submodule.
_Note: If you are familiar with different way for generating the certificates, feel free to use it instead._

```sh
git submodule update --init ./CertificateGeneration
```

### Obtain master certificates

```sh
wget -O ./CertificateGeneration/master.crt https://raw.githubusercontent.com/eclipse-arrowhead/core-java-spring/master/certificates/master.crt
wget -O ./CertificateGeneration/master.p12 https://raw.githubusercontent.com/eclipse-arrowhead/core-java-spring/master/certificates/master.p12
```

### Obtain testcloud2 certificates

```sh
mkdir ./certificates
wget -O ./certificates/testcloud2.crt https://raw.githubusercontent.com/eclipse-arrowhead/core-java-spring/master/certificates/testcloud2/testcloud2.crt
wget -O ./certificates/testcloud2.p12 https://raw.githubusercontent.com/eclipse-arrowhead/core-java-spring/master/certificates/testcloud2/testcloud2.p12
```

### Generate certificates for echo service

```sh
PASSWORD=123456 FOLDER="../certificates/" DOMAIN="aitia" CLOUD="testcloud2" bash ./CertificateGeneration/generate.sh echoserver echoclient
```

## Setting up the rules (and services, etc.)

To set up all required data in the Arrowhead database, at first run:

```sh
python3 echo-setup.py
```

Alternatively, you can launch both parts of the service and receive:
```sh
Interface ID: %d
Provider ID: %d
Service ID: %d
Consumer ID: %d
```

And use `echo-auth.py` to add an intracloud authorization rule to the Arrowhead database:

```sh
python3 echo-auth.py -i %d -p %d -s %d -c %d
```

This has to be run only one (on subsequent runs it does nothing). Then, proceed with relaunching the `echo-client`.

## Launching the service

In two separate terminals run both:

```sh
python3 echo-server.py
```

```sh
python3 echo-client.py
```