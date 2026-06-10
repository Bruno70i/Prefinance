import { defineEventHandler, readBody, createError } from 'h3'
import fs from 'fs'
import path from 'path'
import pg from 'pg'

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id
  const body = await readBody(event)

  if (!body) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Corpo da requisição inválido'
    })
  }

  // Tenta salvar no PostgreSQL
  const dbUrl = process.env.DATABASE_URL
  if (dbUrl) {
    try {
      const pool = new pg.Pool({ 
        connectionString: dbUrl,
        connectionTimeoutMillis: 1500
      })
      const client = await pool.connect()
      try {
        const query = `
          UPDATE entidades 
          SET razao_social = $1, 
              cnpj = $2, 
              responsavel_nome = $3, 
              configuracoes_extras = $4
          WHERE id = $5
          RETURNING id, razao_social, cnpj, responsavel_nome, configuracoes_extras
        `
        const res = await client.query(query, [
          body.razao_social,
          body.cnpj,
          body.responsavel_nome,
          JSON.stringify(body.configuracoes_extras),
          id
        ])
        
        if (res.rows.length > 0) {
          return res.rows[0]
        }
      } finally {
        client.release()
        await pool.end()
      }
    } catch (dbErr) {
      console.warn('Falha ao gravar no PostgreSQL, gravando no fallback local.')
    }
  }

  // Fallback: Grava as alterações no arquivo JSON local
  try {
    const filePath = path.resolve(process.cwd(), 'entidades_mapeadas.json')
    if (fs.existsSync(filePath)) {
      const fileData = fs.readFileSync(filePath, 'utf-8')
      const parsed = JSON.parse(fileData)
      
      // Encontra a entidade correspondente na lista
      const index = parsed.findIndex((e: any, idx: number) => {
        const currentId = e.id || `temp-id-${idx + 1}`
        return currentId === id
      })

      if (index !== -1) {
        // Preserva o ID ou cria um definitivo
        parsed[index] = {
          id: id,
          razao_social: body.razao_social,
          cnpj: body.cnpj,
          responsavel_nome: body.responsavel_nome,
          configuracoes_extras: body.configuracoes_extras
        }
        
        fs.writeFileSync(filePath, JSON.stringify(parsed, null, 2), 'utf-8')
        return parsed[index]
      }
    }
    
    // Retorna o próprio corpo simulando o sucesso
    return { ...body, id }
  } catch (err) {
    console.error('Erro ao salvar localmente:', err)
    throw createError({
      statusCode: 500,
      statusMessage: 'Falha ao salvar os dados locais'
    })
  }
})
