import { defineEventHandler } from 'h3'
import fs from 'fs'
import path from 'path'
import pg from 'pg'

export default defineEventHandler(async (event) => {
  // Tenta carregar do PostgreSQL se configurado
  const dbUrl = process.env.DATABASE_URL
  if (dbUrl) {
    try {
      // Define um timeout curto de conexão (1.5 segundos) para cair no fallback local imediatamente se o Postgres estiver offline
      const pool = new pg.Pool({ 
        connectionString: dbUrl,
        connectionTimeoutMillis: 1500
      })
      const client = await pool.connect()
      try {
        const res = await client.query('SELECT id, razao_social, cnpj, responsavel_nome, configuracoes_extras FROM entidades ORDER BY razao_social ASC')
        return res.rows
      } finally {
        client.release()
        await pool.end()
      }
    } catch (dbErr) {
      console.warn('PostgreSQL offline ou inacessível. Usando fallback de arquivo local imediatamente.')
    }
  }

  // Fallback: Lê o arquivo JSON local gerado no Passo 1
  try {
    const filePath = path.resolve(process.cwd(), 'entidades_mapeadas.json')
    if (fs.existsSync(filePath)) {
      const fileData = fs.readFileSync(filePath, 'utf-8')
      const parsed = JSON.parse(fileData)
      // Adiciona IDs temporários simulando o banco de dados caso não tenham UUIDs
      return parsed.map((ent: any, idx: number) => ({
        id: ent.id || `temp-id-${idx + 1}`,
        razao_social: ent.razao_social,
        cnpj: ent.cnpj,
        responsavel_nome: ent.responsavel_nome,
        configuracoes_extras: ent.configuracoes_extras
      }))
    }
    return []
  } catch (err) {
    console.error('Erro ao ler dados locais:', err)
    return []
  }
})
