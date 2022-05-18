# Active Directory DC Test
This is a OneAgent plugin.

## Metrics
**Active Directory - Response Time** - Response time to query domain controller

**Active Directory - Return Code** - Return code

## Requirements
The plugin runs the following command, so it will need to be available on the host

`dsquery`

The OneAgent must also have been installed with `USER=LocalSystem`. This is the default behavior for new installations >= 1.195

## Configuration Options

This extension will query either a named Domain Controller or an advertised Global Catalog server for computer names. The response time to retrieve the query and the response code.

## Properties
* User Name and Password - These amust be a valid regular user account.  No special permissions required.
* Limit - In large environments you will likely want to set this to some reasonable number.  The plugin to only request a maximum of 1,000 computers.
* Use Global Catalog OR Name of Domain Controller to query - If 'Use Global Catalog' is checked the domain controller entry is ignored.
* Frequency - How often to run in minutes.
* Log Level - Level of logging in the plugin log file.  The default location of the file will be `C:\ProgramData\dynatrace\oneagent\log\plugin`

## Response Codes
* 0 - Everything fine
* 1 - Domain Controller invalid or not reachable
* 2 - Computer Limit Reached
* 3 - Bad username or password

## Things that will cause the plugin to error

There are a number of reasons the plugin will not work.  In all cases any errors will be reported in the Dynatrace console.

1. First and formost the dsquery.exe must be present on the host and in the expected c:\windows\system32 directory.  

Windows servers build with a minimal installation will likely not have dsquery.exe.  Adding the server feature 'Remote Server Administration Tools' -> 'Role Administration Tools' -> 'AD DS and AD LDS Tools' will install dsquery.exe.

2. The plugin needs to use a user name and password to authenticate to the domain controller and sumbit the query.  As such you must provide a user name and password, but the user name does not need elevated permissions or group membership.

3. Last if you choose to specify a domain controller to query instead of using an advertised global catalog server, the domain controller specified must be available when the query is made. Keep in mind that while domain controllers are typically not retired they may go through regular maintenance periods where they are rebooted. During such times the the plugin will record a response code of **1** and the response time will be the time it took for the dsquery command to timeout trying to reach the domain controller. 
