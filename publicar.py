"""Publicação de pacotes binários no GitHub Actions; sem o código do aplicativo."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def montar_executavel(pasta, info, destino):
    if info.get("arquivo") != "Auditoria_Monofasicos.exe":
        raise ValueError("Nome de arquivo inválido")
    if not isinstance(info.get("tamanho"), int) or not 1024 <= info["tamanho"] <= 150 * 1024 * 1024:
        raise ValueError("Tamanho inválido")
    if not re.fullmatch(r"[a-f0-9]{64}", info.get("sha256", "")):
        raise ValueError("Hash inválido")
    completo = pasta / info["arquivo"]
    if completo.exists():
        shutil.copyfile(completo, destino)
    else:
        partes = sorted((pasta / "partes").glob("parte-*.bin"))
        quantidade = (info["tamanho"] + 524287) // 524288
        if [p.name for p in partes] != [f"parte-{i:03}.bin" for i in range(quantidade)]:
            raise ValueError("Partes do pacote ausentes ou fora de sequência")
        with destino.open("wb") as arquivo:
            for parte in partes:
                with parte.open("rb") as origem:
                    shutil.copyfileobj(origem, arquivo)
    if destino.stat().st_size != info["tamanho"]:
        raise ValueError("Pacote incompleto")
    if hashlib.sha256(destino.read_bytes()).hexdigest() != info["sha256"]:
        raise ValueError("SHA-256 do pacote não confere")
    with destino.open("rb") as arquivo:
        if arquivo.read(2) != b"MZ":
            raise ValueError("Pacote não é um executável Windows")


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main():
    versao = json.loads(Path("canal.json").read_text(encoding="utf-8"))["versao"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", versao):
        raise ValueError("Versão inválida")
    pasta = Path("pacotes") / versao
    info = json.loads((pasta / "versao.json").read_text(encoding="utf-8"))
    if info["versao"] != versao:
        raise ValueError("Versão do canal e pacote divergem")
    notas = pasta / "notas.md"
    if not notas.is_file():
        raise ValueError("Notas da versão ausentes")
    tag = "v" + versao
    consulta = subprocess.run(["gh", "release", "view", tag], capture_output=True)
    if consulta.returncode == 0:
        raise ValueError("A versão já existe; nenhuma Release existente será sobrescrita")
    with tempfile.TemporaryDirectory() as pasta_temporaria:
        executavel = Path(pasta_temporaria) / info["arquivo"]
        montar_executavel(pasta, info, executavel)
        gh("release", "create", tag, str(executavel), "--draft", "--target", os.environ["GITHUB_SHA"],
           "--title", "Auditoria Fiscal " + versao, "--notes-file", str(notas))
        release = json.loads(gh("api", f"repos/{os.environ['GH_REPO']}/releases/tags/{tag}"))
        assets = [a for a in release["assets"] if a["name"] == info["arquivo"]]
        if len(assets) != 1 or assets[0].get("digest") != "sha256:" + info["sha256"] or assets[0]["size"] != info["tamanho"]:
            raise ValueError("Asset não passou na verificação do GitHub; a Release permanece como rascunho")
        gh("release", "edit", tag, "--draft=false", "--latest")
        print(f"Publicado: https://github.com/{os.environ['GH_REPO']}/releases/tag/{tag}")


if __name__ == "__main__":
    main()
