<template>
  <a-modal
    v-model:visible="visible"
    title="EDIT TEST PLAN"
    :ok-text="'SAVE'"
    :cancel-text="'CANCEL'"
    :width="600"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <a-form v-if="form" :model="form" layout="vertical">
      <a-form-item label="PLAN NAME" required>
        <a-input
          v-model="form.name"
          placeholder="please input plan name"
          :max-length="100"
          show-word-limit
        />
      </a-form-item>

      <a-form-item label="DESCRIPTION">
        <a-textarea
          v-model="form.description"
          placeholder="please input description"
          :rows="4"
          :max-length="500"
          show-word-limit
        />
      </a-form-item>

      <!-- <a-form-item label="TAGS">
        <a-input
          v-model="form.tags"
          placeholder="please input tags, multiple tags separated by commas"
          :max-length="200"
        />
      </a-form-item> -->

      <a-form-item label="STATUS">
        <a-radio-group v-model="form.status">
          <a-radio :value="1">private</a-radio>
          <a-radio :value="2">public</a-radio>
        </a-radio-group>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import type { EditForm } from '../types'

interface Props {
  modelValue: boolean
  form: EditForm | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'ok': []
  'cancel': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const handleOk = () => {
  emit('ok')
}

const handleCancel = () => {
  emit('cancel')
}
</script>
