# Auditoria Fiscal — versões Windows

Canal público de distribuição do executável da Auditoria Fiscal.

## Instalação e atualização

Baixe **Auditoria_Monofasicos.exe** em [Releases](https://github.com/BergeS7/auditoria-ncm/releases/latest) e salve na pasta do programa.

A partir da versão **16.1.0**, utilize **Verificar atualizações** no próprio programa. O aplicativo confere a integridade do download, guarda a versão anterior e preserva seus relatórios.

Versões anteriores precisam receber o executável 16.1.0 uma vez para habilitar o atualizador.

Este repositório distribui os pacotes Windows. As partes binárias em `pacotes/` servem à publicação automatizada; para instalar, utilize o executável completo disponível em Releases.

## Publicar uma versão nova

1. Compile e valide a próxima versão no projeto do aplicativo.
2. Envie o executável completo para `pacotes/<versao>/Auditoria_Monofasicos.exe`, acompanhado do `versao.json` da compilação e das notas em `notas.md`.
3. Depois do envio completo, atualize `canal.json` com o número da versão (por exemplo, `16.1.1`).
4. O GitHub Actions verifica o pacote, cria a Release em rascunho, confirma o SHA-256 do asset e publica como versão mais recente.

Não reutilize um número de versão já publicado. A automação não substitui assets existentes. O script aceita também partes binárias de 524.288 bytes em `partes/parte-000.bin`, `parte-001.bin` etc.; os usuários devem baixar o executável completo em Releases.
