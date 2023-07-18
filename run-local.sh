#!/bin/bash
pipenv run datasette --reload _data/yumyum.db --metadata metadata.yaml --static static:_static --plugins-dir _plugins --template-dir _templates
