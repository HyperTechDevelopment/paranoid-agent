# MCP — Contrato das Tools

Servidor stdio em `bin/mcp.mjs`. Reaproveita os scripts em `scripts/`; o agente julga, o servidor executa. Sem rede, sem análise, sem probe ativo.

## Configuração do cliente

```json
{
  "mcpServers": {
    "paranoid-agent": {
      "command": "npx",
      "args": ["-y", "paranoid-agent-skill@latest", "mcp"]
    }
  }
}
```

O bin `paranoid-agent-skill` despacha por subcomando: sem arg roda o instalador da skill, com `mcp` sobe o servidor stdio.

## Tools

| Tool | Input | Output |
|---|---|---|
| `secret_sweep` | `path` (default `.`), `include_history` (default true) | JSON redatado: regra, fonte, match parcial. Valor cru nunca sai; o servidor aborta se a redação falhar |
| `port_inventory` | `path` (default `.`) | Listeners locais + `EXPOSE`/compose. Leitura local, sem scan de rede |
| `render_breach_report` | `findings` (objeto no schema de `report-spec.md`), `before` 0–100, `after` 0–100, `write_to` opcional | `{path, bytes, before, after, attacks, ports, leaks, kills}`. Sem `write_to`, grava em temp e devolve o caminho |

## Regras do servidor

- Resolve `python3`, cai para `python`; timeout de 90s e teto de 1MB por execução.
- Segunda barreira de redação no servidor, independente dos scripts.
- `render` valida `before`/`after` como inteiros 0–100 e recusa segredo cru antes de renderizar.
- Escrita em disco só no `render` e só no caminho pedido (ou temp).
- Probes HTTP ativos (matriz A1–A8) ficam fora do MCP: o agente os executa com controle de loopback e dummy.
