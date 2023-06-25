# pi-label-inventory
Python based inventory system with package label generator

# Required Libraries

```
pylabel          : pip3 install pylabels
reportlab        : pip3 install reportlab
simple-term-menu : pip3 install simple-term-menu
```

# Description

## Purpose

I created this to manage all of the boxes that I packed for moving to a new home. I wanted to keep track of each box (package) by:

 - uniquely identifying each one
 - have a description of the contents
 - record the weight of each box

 ## Operations

 This python program will provide three services:

  - Gather package information via command line menu
  - save information into a file based records system (CSV)
  - use all or partial record listings to print out label arrays onto A3 / 8.5" x 11" paper.

  As the data is kept in CSV it can be imported into eg. Excel and used to generate a manifest. Package weights can be summed up to provide a gross weight estimate.

# State

Ver 0.1 Alpha Unstable - in development

# License

GPLv3. Refer to LICENSE file in this repository.
