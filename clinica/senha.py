from dataclasses import dataclass, field
from datatime import datetime
from typing import Optional

@dataclass
class Senha:
    #Representa uma senha de atendimento emitida pela clínica.
    especialidade: str #código da especialidade, ex: 'CG'
    categoria: str #'N' normal ou 'P' preferencial
    numero: int #1,2,3...
    hora_emissao: datetime = field(default_factory=datetime.now)
    hora_chamada: Optional[datetime] = None

    @property
    def codigo(self):
        #Exemplo: CG-N001, CA-P012
        return f'{self.especialidade}-{self.categoria}{self.numero:03d}'
    