#!/usr/bin/env python
import warnings
import os

from coder.crew import Coder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Crea el directorio de salida si no existe
os.makedirs("output", exist_ok=True)

assignment = "Escribe un programa Python para calcular los primeros 1,000 términos \
    de esta serie, multiplicando el total por 4: 1 - 1/3 + 1/5 - 1/7 + ..."


def run():
    """
    Ejecuta la Crew.
    """
    inputs = {
        "assignment": assignment,
    }

    result = Coder().crew().kickoff(inputs=inputs)
    print(result.raw)
