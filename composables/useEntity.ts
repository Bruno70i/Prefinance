import { ref, computed } from 'vue'

export interface Entity {
  id: string
  razao_social: string
  cnpj: string | null
  responsavel_nome: string | null
  configuracoes_extras: Record<string, any>
  created_at?: string
  updated_at?: string
}

// Estado global reativo
const selectedEntity = ref<Entity | null>(null)
const entitiesList = ref<Entity[]>([])
const isLoading = ref<boolean>(false)
const errorMsg = ref<string | null>(null)

export const useEntity = () => {
  // Carrega todas as entidades a partir do banco de dados (API)
  const fetchEntities = async () => {
    isLoading.value = true
    errorMsg.value = null
    try {
      // Faz o fetch assíncrono utilizando o padrão do Nuxt 3
      const { data, error } = await useFetch<Entity[]>('/api/entidades')
      if (error.value) {
        throw new Error(error.value.message || 'Erro ao carregar entidades')
      }
      if (data.value) {
        entitiesList.value = data.value
      }
    } catch (err: any) {
      errorMsg.value = err.message || 'Erro desconhecido'
      console.error('useEntity.fetchEntities:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Seleciona uma entidade específica por ID ou objeto
  const selectEntity = (entity: Entity | null) => {
    selectedEntity.value = entity ? { ...entity } : null
  }

  // Envia as alterações da entidade para o banco de dados (API)
  const saveEntity = async (entityData: Entity) => {
    isLoading.value = true
    errorMsg.value = null
    try {
      const response = await $fetch<Entity>(`/api/entidades/${entityData.id}`, {
        method: 'PUT',
        body: entityData
      })
      
      // Atualiza na lista local para reatividade instantânea
      const index = entitiesList.value.findIndex(e => e.id === response.id)
      if (index !== -1) {
        entitiesList.value[index] = { ...response }
      }
      
      // Se for a entidade atualmente selecionada, atualiza o estado
      if (selectedEntity.value && selectedEntity.value.id === response.id) {
        selectedEntity.value = { ...response }
      }
      
      return response
    } catch (err: any) {
      errorMsg.value = err.message || 'Erro ao salvar alterações da entidade'
      console.error('useEntity.saveEntity:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Cria uma entidade vazia para formulários de criação
  const clearSelection = () => {
    selectedEntity.value = null
  }

  // Exclui uma entidade no banco de dados (API) e remove da lista reativa
  const deleteEntity = async (entityId: string) => {
    isLoading.value = true
    errorMsg.value = null
    try {
      await $fetch(`/api/entidades/${entityId}`, {
        method: 'DELETE'
      })
      
      // Remove da lista reativa instantaneamente
      entitiesList.value = entitiesList.value.filter(e => e.id !== entityId)
      
      // Se for a entidade selecionada no momento, limpa a seleção
      if (selectedEntity.value && selectedEntity.value.id === entityId) {
        selectedEntity.value = null
      }
    } catch (err: any) {
      errorMsg.value = err.message || 'Erro ao excluir entidade'
      console.error('useEntity.deleteEntity:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    selectedEntity,
    entitiesList,
    isLoading,
    errorMsg,
    fetchEntities,
    selectEntity,
    saveEntity,
    clearSelection,
    deleteEntity
  }
}
