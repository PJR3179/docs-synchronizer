# Docs as Code - Confluence

Publish a folder or subfolder of documentation to Confluence.

Create a Confluence Page for each markdown file. Each folder will create a _parent_ page to reflect
the directory structure.

This workflow is adapted for vertexinc's needs from https://github.com/marketplace/actions/docs-as-code-confluence

## Things to Know

- When linking to sections within your markdown files (e.g., `#overview`), use the full GitHub URL. Otherwise, these links will not work correctly after publishing to Confluence. You can manually adjust Confluence hyperlinks after publishing if needed.

- Automatically published docs are not deleted from Confluence.

- Confluence may restrict the width of text in auto-published tables. You may need to manually resize columns to suit your team's preferences.

## Parameters

| Name                  | Description | Required |
|-----------------------| --- | --- |
| `folder`              | The folder to sync | true |
| `username`            | Confluence username or email | true |
| `password`            | Confluence password or [API token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) | true |
| `confluence-base-url` | Your Confluence URL (with `wiki`). Example: `https://mydomain.atlassian.net/wiki` | true |
| `space-key`           | Confluence space key to publish the documentation. Located after `spaces` in the URL. `https://mydomain.atlassian.net/wiki/spaces/<<~1234>>`. <br> Or in _Space settings_ > _Space details_ > _Key_. | true |
| `parent-page-id`      | Page id under which the documentation will be published. Located after `pages` in the URL. `https://mydomain.atlassian.net/wiki/spaces/~1234/pages/<<1234>>/My+Parent+Page` | true |

## Example of workflow

```yml
name: Sync Docs as Code - Confluence
on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
jobs:
  docs-as-code:
    runs-on: ubuntu-latest
    name: Sync Docs as Code - Confluence
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Sync Docs as Code - Confluence
        uses: PJR3179/docs-as-code-confluence@v3
        with:
          folder: 'docs/information_tables'
          username: ${{ secrets.Username}}$ #Email you want to publish from
          password: ${{ secrets.API_TOKEN }}
          confluence-base-url: https://mydomain.atlassian.net/wiki
          space-key: ~1234
          parent-page-id: 123456789
```

## Alternatives

* [markdown-confluence/publish-action](https://github.com/markdown-confluence/publish-action)
* [mbovo/mark2confluence](https://github.com/mbovo/mark2confluence)

**Test**

```bash
npm run test
```

**Build**

```bash
npm run build
```
