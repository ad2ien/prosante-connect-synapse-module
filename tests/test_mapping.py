import aiounittest

from psc_mapping_provider import ProsanteConnectMappingProvider


class ProsanteConnectMappingProviderTestCase(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.config = ProsanteConnectMappingProvider.parse_config(
            {
                "subject_template": "{{ user.sub }}",
                "picture_template": "{{ user.picture }}",
                "localpart_template": "{{ user.preferred_username }}",
                "display_name_template": "{{ user.given_name }} {{ user.family_name }}",
                "email_template": "{{ user.email }}",
                "extra_attributes": {},
                "confirm_localpart": False,
                "default_display_name_suffix": " - not a doctor",
            }
        )

    async def test_real_psc_test(self) -> None:
        mapper = ProsanteConnectMappingProvider(self.config)
        result = await mapper.map_user_attributes(get_a_legit_psc_userinfo(), None, 0)
        assert result["display_name"] == "Fistinien Grominoch - Pédicure-Podologue"
        assert result["localpart"] == "ans20231122132732"

    async def test_real_non_psc_test(self) -> None:
        mapper = ProsanteConnectMappingProvider(self.config)
        result = await mapper.map_user_attributes(get_a_regular_userinfo(), None, 0)
        assert result["display_name"] == "Fistinien Grominoch - not a doctor"
        assert result["localpart"] == "ans20231122132732"


def get_a_legit_psc_userinfo():
    return {
        "Secteur_Activite": "SA07^1.2.250.1.71.4.2.4",
        "sub": "f:550dc1c8-d97b-4b1e-ac8c-8eb4471cf9dd:ANS20231122132732",
        "codeGenreActivite": "GENR01",
        "SubjectOrganization": "CABINET INDIVIDUEL PEDI PODO0023704",
        "Mode_Acces_Raison": "",
        "preferred_username": "ANS20231122132732",
        "codeCivilite": "M",
        "given_name": "Fistinien",
        "Acces_Regulation_Medicale": "FAUX",
        "UITVersion": "1.0",
        "Palier_Authentification": "APPPRIP3^1.2.250.1.213.1.5.1.1.1",
        "SubjectRefPro": {
            "exercices": [
                {
                    "codeProfession": "80",
                    "codeCategorieProfessionnelle": "C",
                    "codeCiviliteDexercice": "",
                    "nomDexercice": "Grominoch",
                    "prenomDexercice": "Fistinien",
                    "codeTypeSavoirFaire": "",
                    "codeSavoirFaire": "",
                    "activities": [
                        {
                            "codeModeExercice": "L",
                            "codeSecteurDactivite": "SA07",
                            "codeSectionPharmacien": "",
                            "codeRole": "",
                            "codeGenreActivite": "GENR01",
                            "numeroSiretSite": "",
                            "numeroSirenSite": "",
                            "numeroFinessSite": "",
                            "numeroFinessetablissementJuridique": "",
                            "identifiantTechniqueDeLaStructure": "R81311",
                            "raisonSocialeSite": "CABINET INDIVIDUEL PEDI PODO0023704",
                            "enseigneCommercialeSite": "",
                            "complementDestinataire": "CABINET INDIVIDUEL PEDI PODO",
                            "complementPointGeographique": "",
                            "numeroVoie": "2",
                            "indiceRepetitionVoie": "",
                            "codeTypeDeVoie": "R",
                            "libelleVoie": "DE LA CHAUSSURE",
                            "mentionDistribution": "",
                            "bureauCedex": "75015 PARIS",
                            "codePostal": "75015",
                            "codeCommune": "",
                            "codePays": "99000",
                            "telephone": "",
                            "telephone2": "",
                            "telecopie": "",
                            "adresseEMail": "",
                            "codeDepartement": "",
                            "ancienIdentifiantDeLaStructure": "499700237045007",
                            "autoriteDenregistrement": "CNOPP/CNOPP/CNOPP",
                        }
                    ],
                }
            ]
        },
        "SubjectOrganizationID": "R81311",
        "SubjectRole": ["80^1.2.250.1.213.1.1.5.5"],
        "PSI_Locale": "1.2.250.1.213.1.3.1.1",
        "otherIds": [
            {"identifiant": "ANS20231122132732", "origine": "EDIT", "qualite": 1}
        ],
        "SubjectNameID": "ANS20231122132732",
        "family_name": "Grominoch",
    }


def get_a_regular_userinfo():
    return {
        "sub": "f:550dc1c8-d97b-4b1e-ac8c-8eb4471cf9dd:ANS20231122132732",
        "preferred_username": "ANS20231122132732",
        "codeCivilite": "M",
        "given_name": "Fistinien",
        "SubjectNameID": "ANS20231122132732",
        "family_name": "Grominoch",
    }
