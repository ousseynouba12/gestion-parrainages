from pydantic import BaseModel

class ElecteurTemporaireBase(BaseModel):
    numElecteur: str
    numCIN: str
    nom: str
    prenom: str
    dateNaissance: str
    lieuNaissance: str
    sexe: str
    bureauVote: str
    idTentative: int
    erreur: str

class ElecteurTemporaire(ElecteurTemporaireBase):
    class Config:
        from_attributes = True

