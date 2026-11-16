# Instalar só a skill (sem MCP)

Copie o bloco abaixo e cole no seu agente. Ele instala os arquivos da skill e não configura nenhum servidor MCP.

```text
Instale apenas a skill paranoid-agent (sem MCP):

1. Rode: npx -y paranoid-agent-skill@latest --dir <skills-dir>
   Use o diretório de skills do meu cliente; se não souber qual é, me pergunte antes.
   Referências: OpenCode ~/.agents/skills, Claude Code ~/.claude/skills,
   Codex ~/.codex/skills, ou a pasta de skills do projeto atual.
2. Confirme que <skills-dir>/paranoid-agent contém SKILL.md, README.md,
   assets/, examples/, references/ e scripts/.
3. Me reporte o caminho final. Não configure nenhum servidor MCP.
```

Depois de instalado, ative a skill dizendo ao agente: `desconfie de tudo neste projeto`.

Quer também o servidor MCP? Veja `INSTALL_MCP.md`. Para os dois juntos, execute os dois prompts.
