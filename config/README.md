OF-PControls Configuration
============

There are two configuration files here:
/etc/ofpcontrols.conf
/etc/ryu.d/ofpcontrols.conf

/etc/ryu.d/
------
This is a directory where you can create .conf files for ryu to load.
The problem is that the oslo.config package that ryu requires that you 
register all possible supported options in your app code.  This makes it
impossible to use this as a user-edited conf file.

But what you *can* do is register an option that points to a user-edited 
conf file that you can load with other modules.
 
For convenience, I named this file after this app's module name and put the
single-option conf file in /etc/ryu.d/.

/etc/ofpcontrols.conf
----------------
This is the main config file for this app.   This file will hold global settings
about your network as well as the rules that you want to load on startup.

I will probably also hook the API into this so that when you add a rule or change
the HOMENET from the API, this file will get updated.  But I'm not sure if that's **good**
or **bad**.
