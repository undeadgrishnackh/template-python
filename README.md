# Python template

This Python template is wrapped into a cookiecutter scaffolding. To use it you need to have `cookiecutter` installed. If you don't have it yet, you can install it via pip, brew, or other package managers. Read more at [cookiecutter's installation guide 📖](https://cookiecutter.readthedocs.io/en/latest/installation.html).

```bash
pip install python3 -m pip install --user cookiecutter
```

👉 Homebrew (Mac OS X only):

```
brew install cookiecutter
```

## Configuration Parameters

| Parameter        | Default   | Options               | Description                            |
| ---------------- | --------- | --------------------- | -------------------------------------- |
| kata_name        | DummyKata | string                | Name for the kata/project              |
| use_dated_prefix | yes       | yes, no               | Add YYYYMMDD prefix to directory name  |
| directory_name   | Generated | string                | Override auto-generated directory name |
| open_ide         | none      | none, vscode, pycharm | IDE to open after generation           |

## Usage Examples

The cookiecutter command below shows different usage examples. The final result is a python scaffolded project ready for development following the best practices we showcase in the SW Craftsmanship Dojo®.

⚠️ This cookiecutter is at a level of a yellow 🟡 belt. No Docker and all the other DevOps jeweleris here.

### Standard kata (dated prefix, no IDE):
```bash
cookiecutter gh:/undeadgrishnackh/template-python
```

### Clean directory for monorepo integration:
```bash
cookiecutter gh:/undeadgrishnackh/template-python \
  use_dated_prefix=no \
  kata_name=trading-engine
```

### Interactive development with VS Code:
```bash
cookiecutter gh:/undeadgrishnackh/template-python \
  open_ide=vscode
```

### 5D-Wave agent usage (automation safe):
```bash
cookiecutter gh:/undeadgrishnackh/template-python \
  use_dated_prefix=no \
  kata_name=source
# No IDE opens, terminal returns control immediately
```
