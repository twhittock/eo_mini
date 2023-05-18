# EO Mini

_Component to integrate with [EO Mini chargers](https://www.eocharging.com/support/home-charging/eo-mini)._

## Installation (HACS - preferred)

1. Add this repo as a custom repository in HACS. https://hacs.xyz/docs/faq/custom_repositories/
2. Add EO Mini Charger component.
3. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "EO Mini" enter username & password from the app.

## Installation (manual)

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `eo_mini`.
4. Download _all_ the files from the `custom_components/eo_mini/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "EO Mini"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/eo_mini/translations/en.json
custom_components/eo_mini/translations/nb.json
custom_components/eo_mini/translations/sensor.nb.json
custom_components/eo_mini/__init__.py
custom_components/eo_mini/api.py
custom_components/eo_mini/binary_sensor.py
custom_components/eo_mini/config_flow.py
custom_components/eo_mini/const.py
custom_components/eo_mini/manifest.json
custom_components/eo_mini/sensor.py
custom_components/eo_mini/switch.py
```

## Configuration is done in the UI


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)
