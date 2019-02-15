# Configuration
Currently, you can only configure the layout of the website.

## Layout
There are some files to configure the layout of the website and the knx bus. In the configuration file `layout.yaml`, you can specify the
bus addresses of your knx bus and organize them in logical groups.

### `layout.yaml`
This file is created by the user. It contains the layout and knx group addresses. Also, it defines how the addresses are organized on the
website into logical groups and what symbols are used to represent them.

### `layout-example.yaml`
This file is an example to show how a layout could look like.

### `schema-layout.yaml` and `metaschemata-devices.yaml`
These files allow the user to validate their `layout.yaml`-file so they can be certain, their file is formatted correctly. For validation
[Rx](http://rx.codesimply.com) is used. To validate your file in terminal, you can use 
[schema-validator](https://github.com/larslockefeer/schema-validator).

```
gem install schema-validator
schema-validator -m metaschemata-devices.yaml -s schema-layout.yaml -f layout.yaml
```
