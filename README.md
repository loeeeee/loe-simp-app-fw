# loe-simp-app-fw
A super simple python app framework that includes a logger and a config management

## Behavior

When the package is imported in other modules,

- duplicate a config sample located in the project root folder
- read from config file in the project root path

## Ethics

> For most cases, packages and modules shouldn't need to care about or depend on the calling environment's location; they should be designed to function independently of where and how they are called.
