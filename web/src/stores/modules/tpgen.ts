import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SavedPlanResp } from '@/apis/tpgen'

export const useTpgenStore = defineStore('tpgen', () => {
  // 编辑模式相关状态
  const editMode = ref(false)
  const editingPlan = ref<SavedPlanResp | null>(null)

  /**
   * 设置编辑模式
   * @param plan 要编辑的计划数据
   */
  const setEditMode = (plan: SavedPlanResp) => {
    editMode.value = true
    editingPlan.value = plan
    console.log('[TpgenStore] 进入编辑模式:', plan)
  }

  /**
   * 清除编辑模式
   */
  const clearEditMode = () => {
    editMode.value = false
    editingPlan.value = null
    console.log('[TpgenStore] 清除编辑模式')
  }

  return {
    editMode,
    editingPlan,
    setEditMode,
    clearEditMode,
  }
})

