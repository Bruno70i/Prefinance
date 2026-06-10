import { b as defineEventHandler } from '../../_/nitro.mjs';
import fs from 'fs';
import path from 'path';
import pg from 'pg';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';

const index_get = defineEventHandler(async (event) => {
  const dbUrl = process.env.DATABASE_URL;
  if (dbUrl) {
    try {
      const pool = new pg.Pool({
        connectionString: dbUrl,
        connectionTimeoutMillis: 1500
      });
      const client = await pool.connect();
      try {
        const res = await client.query("SELECT id, razao_social, cnpj, responsavel_nome, configuracoes_extras FROM entidades ORDER BY razao_social ASC");
        return res.rows;
      } finally {
        client.release();
        await pool.end();
      }
    } catch (dbErr) {
      console.warn("PostgreSQL offline ou inacess\xEDvel. Usando fallback de arquivo local imediatamente.");
    }
  }
  try {
    const filePath = path.resolve(process.cwd(), "entidades_mapeadas.json");
    if (fs.existsSync(filePath)) {
      const fileData = fs.readFileSync(filePath, "utf-8");
      const parsed = JSON.parse(fileData);
      return parsed.map((ent, idx) => ({
        id: ent.id || `temp-id-${idx + 1}`,
        razao_social: ent.razao_social,
        cnpj: ent.cnpj,
        responsavel_nome: ent.responsavel_nome,
        configuracoes_extras: ent.configuracoes_extras
      }));
    }
    return [];
  } catch (err) {
    console.error("Erro ao ler dados locais:", err);
    return [];
  }
});

export { index_get as default };
//# sourceMappingURL=index.get.mjs.map
