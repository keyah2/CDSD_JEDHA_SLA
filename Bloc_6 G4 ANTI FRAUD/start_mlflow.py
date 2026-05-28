"""
Script de démarrage MLflow.
Lance : python start_mlflow.py
Puis ouvre : http://localhost:5000
"""
import os
import sys
import subprocess

# Dossier du script = racine du projet
ROOT = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(ROOT, "mlflow.db")
URI  = f"sqlite:///{DB}"

print(f"Backend : {URI}")
print("Lancement de MLflow UI...")
print("Ouvre http://localhost:5000 dans ton navigateur")
print("Appuie sur CTRL+C pour arrêter\n")

subprocess.run([
    sys.executable, "-m", "mlflow", "ui",
    "--backend-store-uri", URI,
    "--port", "5000"
])
