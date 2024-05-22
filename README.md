# eimis-prosante-connect-module

A synapse module used by EIMIS to filter and map users registered through Prosanté Connect

## OIDC configuration

Todo: how to configure keycloak to have the same token than PSC?

## User info

<https://industriels.esante.gouv.fr/produits-et-services/pro-sante-connect/userinfo>

## Dev

### lint

```bash
tox -e check_codestyle
```

### test

```bash
tox -e py
```
