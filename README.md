DNSPC
=====

DNS based parental controls

dnspc provides a rule engine to allow you to block or redirect DNS requests to selected domains for specific devices during a specified time frame.  The motivation is not for content filtering, but rather for enforcing rules surrounding use of devices.  E.g. my daughter needs to be able to reach Google Docs for homework, but I want to restrict access to Netflix and YouTube during that time.

Also, because this acts as the DNS server, it can log all requests and report usage per device.

***DHCP Server***
For the first iteration of this, you can just set the name-server or dns-server options on your DHCP server to the IP of the server where this app is installed.

The dnspc app will snoop dhcp packets on the network to learn what is on the network to simplify rule creation.

Eventually, I will add a pyDHCP server to this so you can simply shut off your existing one.
