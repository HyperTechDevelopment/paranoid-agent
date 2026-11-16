# Instalar só o MCP (sem os arquivos da skill)

Copie o bloco abaixo e cole no seu agente. Ele registra o servidor MCP e não copia nenhum arquivo da skill.

Requisito: Node 18+ no PATH e Python (`python3` ou `python`) no PATH.

```text
Instale apenas o servidor MCP paranoid-agent (sem copiar a skill):

1. Descubra onde fica o arquivo de configuração MCP do meu cliente
   (opencode.json, .claude.json, config.toml do Codex ou equivalente).
   Se não souber, me pergunte antes de editar.
2. Adicione o servidor "paranoid-agent":
   comando: npx
   argumentos: -y, paranoid-agent-skill@latest, mcp
   (transporte stdio, sem variável de ambiente)
3. Valide subindo o servidor e listando as tools: tem que aparecer
   secret_sweep, port_inventory e render_breach_report.
   Se alguma faltar, me mostre o erro em vez de seguir.
4. Me reporte onde registrou. Não copie nenhum arquivo da skill.
```

Depois de instalado, use a partir de qualquer agente com acesso às tools. O fluxo completo com julgamento (score, kill-list) está na skill; veja `INSTALL_SKILL.md`. Para os dois juntos, execute os dois prompts.
