<template>
  <a-modal
    v-model:visible="visible"
    title="分配角色"
    :mask-closable="false"
    :esc-to-close="false"
    :width="width >= 600 ? 600 : '100%'"
    draggable
    @before-ok="save"
    @close="reset"
  >
    <a-alert v-if="form.isSystem" type="warning" class="mb-4">
      该用户为系统用户，拥有所有权限，无需分配角色。
    </a-alert>
    <GiForm ref="formRef" v-model="form" :options="options" :columns="columns" />
  </a-modal>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import { useWindowSize } from '@vueuse/core'
import { getUser, updateUserRole } from '@/apis/system'
import { type Columns, GiForm, type Options } from '@/components/GiForm'
import { useResetReactive } from '@/hooks'
import { useRole } from '@/hooks/app'

const emit = defineEmits<{
  (e: 'save-success'): void
}>()

const { width } = useWindowSize()
const dataId = ref('')
const visible = ref(false)
const formRef = ref<InstanceType<typeof GiForm>>()
const { roleList, getRoleList } = useRole()

const options: Options = {
  form: { size: 'large' },
  btns: { hide: true },
}

const [form, resetForm] = useResetReactive({})

const columns: Columns = reactive([
  {
    label: '角色',
    field: 'roleIds',
    type: 'select',
    options: roleList,
    props: {
      multiple: true,
      allowClear: true,
      allowSearch: { retainInputValue: true },
      placeholder: '请选择角色',
    },
    rules: [
      { 
        required: true, 
        message: '请选择角色',
        validator: (value: any, callback: any) => {
          // 系统用户不需要验证角色
          if (form.isSystem) {
            callback()
          } else if (!value || value.length === 0) {
            callback('请选择角色')
          } else {
            callback()
          }
        }
      }
    ],
  },
])

// 重置
const reset = () => {
  formRef.value?.formRef?.resetFields()
  resetForm()
}

// 保存
const save = async () => {
  try {
    // 系统用户不允许修改角色
    if (form.isSystem) {
      Message.warning('系统用户拥有所有权限，无需分配角色')
      return false
    }
    
    const isInvalid = await formRef.value?.formRef?.validate()
    if (isInvalid) return false
    await updateUserRole({ roleIds: form.roleIds }, dataId.value)
    Message.success('分配成功')
    emit('save-success')
    return true
  } catch (error) {
    return false
  }
}

// 初始化
const onOpen = async (id: string) => {
  reset()
  dataId.value = id
  if (!roleList.value.length) {
    await getRoleList()
  }
  const { data } = await getUser(id)
  Object.assign(form, data)
  visible.value = true
}

defineExpose({ onOpen })
</script>

<style scoped lang="scss"></style>
