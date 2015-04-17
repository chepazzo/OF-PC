DNSPC
=====

DNS based parental controls

dnspc provides a rule engine to allow you to block or redirect DNS requests to selected domains for specific devices during a specified time frame.  The motivation is not for content filtering, but rather for enforcing rules surrounding use of devices.  E.g. my daughter needs to be able to reach Google Docs for homework, but I want to restrict access to Netflix and YouTube during that time.

Also, because this acts as the DNS server, it can log all requests and report usage per device.

Rules
=====
To create a rule, you specify the:
* __source.__
  Type in IP address or select from drop list of known (onboarded) hosts.
* __destination.__
  Type in a destination you want to control.
  e.g. `*.netflix.com`
* __action.__
  Select an action to take when this rule matches (drop, allow, redirect).
* __When.__
  Select days of week and time period when this rule will be in effect.


Onboard
=======
If you direct any device to /onboard, the app will grab your IP address, MAC address (if you are on the same subnet), and hostname.  You can modify these values as well as designate an "Owner" for the device (this will help in identifying devices later).


***DHCP Server***
For the first iteration of this, you can just set the name-server or dns-server options on your DHCP server to the IP of the server where this app is installed.

Eventually, I will add a pyDHCP server to this so you can simply shut off your existing one.  The dnspc app might also snoop dhcp packets on the network to learn what is on the network to simplify rule creation.

ToDo
====
1. Add snooze button to temporarily disable or enable a rule
    * Snooze would automatically revert after alloted time.
2. Create reports based on query logs.
3. Add functionality to allow user to group a list of domains in a single rule
    * e.g. { "name":"youtube","domains":["\*.youtube.com","\*.googlevideo.com"] }
4. Improve performance
5. Respond with user-defined data for matches to onboarded hosts/IPs.
6. Allow re-ordering of rules.
7. Better handling of behavior if multiple rules match.

