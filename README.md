# Python template

This Python template is wrapped into a cookiecutter scaffolding. To use it:

```bash
cookiecutter https://github.com/undeadgrishnackh/template-python.git
```

## Configuration Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| kata_name | DummyKata | string | Name for the kata/project |
| use_dated_prefix | yes | yes, no | Add YYYYMMDD prefix to directory name |
| directory_name | Generated | string | Override auto-generated directory name |
| open_ide | none | none, vscode, pycharm | IDE to open after generation |

## Usage Examples

### Standard kata (dated prefix, no IDE):
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_
```

### Clean directory for monorepo integration:
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_ \
  use_dated_prefix=no \
  kata_name=trading-engine
```

### Interactive development with VS Code:
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_ \
  open_ide=vscode
```

### 5D-Wave agent usage (automation safe):
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_ \
  use_dated_prefix=no \
  kata_name=source
# No IDE opens, terminal returns control immediately
```
