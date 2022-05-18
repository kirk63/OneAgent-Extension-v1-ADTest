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

