import logging
from typing import Any, Dict, List, Optional

import attr
from authlib.oidc.core import UserInfo
from jinja2 import Environment, Template
from synapse.config import ConfigError
from synapse.handlers.oidc import OidcMappingProvider, Token, UserAttributeDict
from synapse.types import map_username_to_mxid_localpart
from synapse.util.templates import _localpart_from_email_filter

logger = logging.getLogger(__name__)


# Used to clear out "None" values in templates
def jinja_finalize(thing: Any) -> Any:
    return thing if thing is not None else ""


env = Environment(finalize=jinja_finalize)
env.filters.update(
    {
        "localpart_from_email": _localpart_from_email_filter,
    }
)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ProsanteConnectMappingConfig:
    subject_template: Template
    picture_template: Template
    localpart_template: Optional[Template]
    display_name_template: Optional[Template]
    email_template: Optional[Template]
    extra_attributes: Dict[str, Template]
    confirm_localpart: bool = False


class ProsanteConnectMappingProvider(OidcMappingProvider[ProsanteConnectMappingConfig]):
    def __init__(self, parsed_config: ProsanteConnectMappingConfig):
        self._config = parsed_config

    @staticmethod
    def parse_config(config: dict) -> ProsanteConnectMappingConfig:
        def parse_template_config_with_claim(
            option_name: str, default_claim: str
        ) -> Template:
            template_name = f"{option_name}_template"
            template = config.get(template_name)
            if not template:
                # Convert the legacy subject_claim into a template.
                claim = config.get(f"{option_name}_claim", default_claim)
                template = "{{ user.%s }}" % (claim,)

            try:
                return env.from_string(template)
            except Exception as e:
                raise ConfigError("invalid jinja template", path=[template_name]) from e

        subject_template = parse_template_config_with_claim("subject", "sub")
        picture_template = parse_template_config_with_claim("picture", "picture")

        def parse_template_config(option_name: str) -> Optional[Template]:
            if option_name not in config:
                return None
            try:
                return env.from_string(config[option_name])
            except Exception as e:
                raise ConfigError("invalid jinja template", path=[option_name]) from e

        localpart_template = parse_template_config("localpart_template")
        display_name_template = parse_template_config("display_name_template")
        email_template = parse_template_config("email_template")

        extra_attributes = {}  # type Dict[str, Template]
        if "extra_attributes" in config:
            extra_attributes_config = config.get("extra_attributes") or {}
            if not isinstance(extra_attributes_config, dict):
                raise ConfigError("must be a dict", path=["extra_attributes"])

            for key, value in extra_attributes_config.items():
                try:
                    extra_attributes[key] = env.from_string(value)
                except Exception as e:
                    raise ConfigError(
                        "invalid jinja template", path=["extra_attributes", key]
                    ) from e

        confirm_localpart = config.get("confirm_localpart") or False
        if not isinstance(confirm_localpart, bool):
            raise ConfigError("must be a bool", path=["confirm_localpart"])

        return ProsanteConnectMappingConfig(
            subject_template=subject_template,
            picture_template=picture_template,
            localpart_template=localpart_template,
            display_name_template=display_name_template,
            email_template=email_template,
            extra_attributes=extra_attributes,
            confirm_localpart=confirm_localpart,
        )

    def get_remote_user_id(self, userinfo: UserInfo) -> str:
        return self._config.subject_template.render(user=userinfo).strip()

    async def map_user_attributes(
        self, userinfo: UserInfo, token: Token, failures: int
    ) -> UserAttributeDict:
        localpart = None
        logger.info("PSC Mapping user attributes with userinfo %s", userinfo)

        if self._config.localpart_template:
            localpart = self._config.localpart_template.render(user=userinfo).strip()

            # Ensure only valid characters are included in the MXID.
            localpart = map_username_to_mxid_localpart(localpart)

            # Append suffix integer if last call to this function failed to produce
            # a usable mxid.
            localpart += str(failures) if failures else ""

        def render_template_field(template: Optional[Template]) -> Optional[str]:
            if template is None:
                return None
            return template.render(user=userinfo).strip()

        display_name = render_template_field(self._config.display_name_template)
        if display_name == "":
            display_name = None

        if (
            "SubjectRefPro" in userinfo
            and "exercices" in userinfo["SubjectRefPro"]
            and len(userinfo["SubjectRefPro"]["exercices"]) > 0
            and "codeProfession" in userinfo["SubjectRefPro"]["exercices"][0]
        ):
            display_name += " - " + get_activity_from_code(
                userinfo["SubjectRefPro"]["exercices"][0]["codeProfession"]
            )

        emails: List[str] = []
        email = render_template_field(self._config.email_template)
        if email:
            emails.append(email)

        picture = self._config.picture_template.render(user=userinfo).strip()

        return UserAttributeDict(
            localpart=localpart,
            display_name=display_name,
            emails=emails,
            picture=picture,
            confirm_localpart=self._config.confirm_localpart,
        )


def get_activity_from_code(code: str) -> str:
    activities = {
        # https://mos.esante.gouv.fr/NOS/TRE_G15-ProfessionSante/TRE_G15-ProfessionSante.pdf
        "10": "Médecin",
        "21": "Pharmacien",
        "26": "Audioprothésiste",
        "28": "Opticien-Lunetier",
        "31": "Assistant dentaire",
        "32": "Physicien médical",
        "35": "Aide-soignant",
        "36": "Ambulancier",
        "37": "Auxiliaire de puériculture",
        "38": "Préparateur en pharmacie hospitalière",
        "39": "Préparateur en pharmacie (officine)",
        "40": "Chirurgien-Dentiste",
        "50": "Sage-Femme",
        "60": "Infirmier",
        "69": "Infirmier psychiatrique",
        "70": "Masseur-Kinésithérapeute",
        "80": "Pédicure-Podologue",
        "81": "Orthoprothésiste",
        "82": "Podo-Orthésiste",
        "83": "Orthopédiste-Orthésiste",
        "84": "Oculariste",
        "85": "Epithésiste",
        "86": "Technicien de laboratoire médical",
        "91": "Orthophoniste",
        "92": "Orthoptiste",
        # "93": "Psychologue",
        "94": "Ergothérapeute",
        "95": "Diététicien",
        "96": "Psychomotricien",
        "98": "Manipulateur ERM",
        # https://mos.esante.gouv.fr/NOS/TRE_R94-ProfessionSocial/TRE_R94-ProfessionSocial.pdf
        "200": "Assistant de service social",
        "201": "Auxiliaire de vie sociale",
        "202": "Technicien de l'intervention sociale et familiale",
        "203": "Conseiller en économie sociale et familiale",
        "204": "Médiateur familial",
        "205": "Assistant familial",
        "206": "Aide médico-psychologique (AMP)",
        "207": "Moniteur éducateur",
        "208": "Educateur de jeunes enfants",
        "209": "Educateur spécialisé",
        "210": "Educateur technique spécialisé",
        "211": "Aide à domicile Aide à domicile",
        "212": "Assistant(e) maternel(le)",
        "213": "Accompagnant éducatif et social",
        "41": "Assistant de service social",
        "42": "Auxiliaire de vie sociale",
        "43": "Technicien de l'intervention sociale et familiale",
        "44": "Conseiller en économie sociale et familiale Conseiller ESF",
        "45": "Médiateur familial",
        "46": "Assistant familial",
        "47": "Aide médico-psychologique (AMP)",
        "48": "Moniteur éducateur",
        "49": "Educateur de jeunes enfants",
        "51": "Educateur spécialisé",
        "52": "Educateur technique spécialisé",
        "53": "Accompagnant éducatif et social",
        # https://mos.esante.gouv.fr/NOS/TRE_R95-UsagerTitre/TRE_R95-UsagerTitre.pdf
        "171": "Ostéopathe",
        "173": "Chiropracteur",
        "172": "Psychothérapeute",
        "193": "Psychologue",
        "194": "Conseiller en génétique",
        "71": "Ostéopathe",
        "72": "Psychothérapeute",
        "73": "Chiropracteur",
        "93": "Psychologue",
        "97": "Conseiller en génétique",
    }

    return activities.get(code, "PSC")
