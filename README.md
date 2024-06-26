# EIMIS Pro Santé Connect module

![Matrix](https://img.shields.io/badge/matrix-000000?logo=Matrix&logoColor=white)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/eimis-ans/eimis-prosante-connect-module/lint.yml?label=lint&logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/eimis-ans/eimis-prosante-connect-module/test.yml?label=test&logo=github)
![License](https://img.shields.io/badge/license-Apache%202-blue.svg?logo=apache)

A Synapse module used by EIMIS to map users registered through Pro Santé Connect. It will mainly add the main activity to display name. It can be used with other ID provider, the display name will then be suffixed with `default_display_name_suffix` config parameter.

## OIDC configuration

Todo: how to configure Keycloak to have the same token than PSC?

## Synapse configuration

```yaml
  - idp_id: psc
    idp_name: "Pro Santé Connect"
    idp_icon: "{{ mxc_psc.stdout }}"
    discover: false
    issuer: "{{ prosante_connect.issuer }}"
    authorization_endpoint: "{{ prosante_connect.authorization_endpoint }}"
    token_endpoint: "{{ prosante_connect.token_endpoint }}"
    userinfo_endpoint: "{{ prosante_connect.userinfo_endpoint }}"
    jwks_uri: "{{ prosante_connect.jwks_uri }}"
    client_id: "{{ prosante_connect.client_id }}"
    client_secret: "{{ prosante_connect.client_secret }}"
    user_profile_method: userinfo_endpoint
    scopes: ["openid", "scope_all"]
    user_mapping_provider:
      module: synapse.psc_mapping_provider.ProsanteConnectMappingProvider
      config:
        localpart_template: "{{ user.preferred_username }}"
        display_name_template: "{{ user.given_name }} {{ user.family_name }}"
        email_template: "{{ user.email }}"
        default_display_name_suffix: " - not a doctor"
    backchannel_logout_enabled: true # Optional
```

Usually used with `enable_set_displayname` set to false.

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
