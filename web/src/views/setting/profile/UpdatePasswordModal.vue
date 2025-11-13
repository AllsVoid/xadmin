<template>
  <a-modal
    v-model:visible="visible"
    title="修改密码"
    :mask-closable="false"
    :esc-to-close="false"
    :width="width >= 500 ? 500 : '100%'"
    draggable
    @before-ok="save"
    @ok="saveAfter"
    @close="reset"
  >
    <GiForm ref="formRef" v-model="form" :options="options" :columns="columns" />
  </a-modal>
</template>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import { Message } from '@arco-design/web-vue'
import NProgress from 'nprogress'
import { updateUserPassword } from '@/apis'
import { encryptByRsa } from '@/utils/encrypt'
import { useUserStore } from '@/stores'
import { type Columns, GiForm, type Options } from '@/components/GiForm'
import { useResetReactive } from '@/hooks'
import modalErrorWrapper from '@/utils/modal-error-wrapper'
import router from '@/router'

const { width } = useWindowSize()
const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const visible = ref(false)
const formRef = ref<InstanceType<typeof GiForm>>()

const options: Options = {
  form: { size: 'large' },
  btns: { hide: true },
}

const [form, resetForm] = useResetReactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const columns: Columns = reactive([
  {
    label: '当前密码',
    field: 'oldPassword',
    type: 'input-password',
    props: {
      placeholder: '请输入当前密码',
    },
    rules: [{ required: true, message: '请输入当前密码' }],
    hide: () => {
      return !userInfo.value.pwdResetTime
    },
  },
  {
    label: '新密码',
    field: 'newPassword',
    type: 'input-password',
    props: {
      placeholder: '请输入新密码（至少8位）',
    },
    rules: [
      { required: true, message: '请输入新密码' },
      { minLength: 8, message: '密码长度至少为8位' },
      {
        validator: (value, callback) => {
          if (form.oldPassword && value === form.oldPassword) {
            callback('新密码不能与当前密码相同')
          } else {
            callback()
          }
        },
      },
    ],
  },
  {
    label: '确认新密码',
    field: 'confirmPassword',
    type: 'input-password',
    props: {
      placeholder: '请再次输入新密码',
    },
    rules: [
      { required: true, message: '请再次输入新密码' },
      {
        validator: (value, callback) => {
          if (value !== form.newPassword) {
            callback('两次输入的密码不一致')
          } else {
            callback()
          }
        },
      },
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
  const isInvalid = await formRef.value?.formRef?.validate()
  if (isInvalid) return false
  
  try {
    // 验证两次密码是否一致
    if (form.newPassword !== form.confirmPassword) {
      Message.error('两次输入的密码不一致')
      return false
    }

    // 验证新密码与旧密码是否相同
    if (form.oldPassword && form.newPassword === form.oldPassword) {
      Message.error('新密码不能与当前密码相同')
      return false
    }

    // 调用API修改密码
    await updateUserPassword({
      oldPassword: encryptByRsa(form.oldPassword) || '',
      newPassword: encryptByRsa(form.newPassword) || '',
    })
    
    return true
  } catch (error) {
    return false
  }
}

// 保存后的处理
const saveAfter = async () => {
  modalErrorWrapper({
    title: '提示',
    content: '密码修改成功！请保存好新密码，并使用新密码重新登录',
    maskClosable: false,
    escToClose: false,
    okText: '重新登录',
    async onOk() {
      NProgress.done()
      await userStore.logoutCallBack()
      await router.replace('/login')
    },
  })
}

// 打开弹窗
const open = () => {
  reset()
  visible.value = true
}

defineExpose({ open })
</script>

<style scoped lang="scss">
:deep(.arco-form-item-message) {
  font-size: 12px;
}
</style>

